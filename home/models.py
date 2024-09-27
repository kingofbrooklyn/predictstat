from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.core.validators import MinValueValidator
from pandas import read_csv, DataFrame
import pickle
import io
from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
import plotly.express as px
from pathlib import Path
from itertools import chain

# Convert model to dictionary
def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

# Get the maximum string character length of select choices
def max_length(choices):
    if None in dict(choices).keys():
        choices_dict = dict(choices)
        choices_dict.pop(None)
        max_len = len(max(choices_dict.keys(), key=len))
        return max_len
    return len(max(dict(choices).keys(), key=len)) 

### Base ###

class Base(models.Model):

    class Meta:
        abstract = True

    @property
    def key(self):
        key = self.__class__.__name__.lower()
        return key

    def save(self, *args, **kwargs):
        ### Delete old versions of the file on storage system ###
        # Determine if this is an existing entry
        try:
            old = type(self).objects.get(id=self.id)
            # Get a list of the file fields, and references to existing files
            file_fields = [field for field in old._meta.fields if field.get_internal_type() == 'FileField']
            files_to_delete = []
            for file_field in file_fields:
                file_field_old = getattr(old, file_field.name)
                file_field_new = getattr(self, file_field.name)
                # If the old file is not the same as the new, add it to the list to delete
                if file_field_old != file_field_new:
                    files_to_delete += [getattr(old, file_field.name)]
            # Run the save
            super().save(*args, **kwargs)
            # Delete old files
            for file_to_delete in files_to_delete:
                file_to_delete.delete(False)
        except:
            # New entry: run the save
            super().save(*args, **kwargs)

    @staticmethod
    def post_delete_delete_file_fields(sender, instance, **kwargs):
        file_fields = [field for field in instance._meta.fields if field.get_internal_type() == 'FileField']
        # Pass false so FileField doesn't save the model.
        for file_field in file_fields:
            if getattr(instance, file_field.name):
                getattr(instance, file_field.name).delete(False)

    ### user ###
    USER_BLANK = True
    user = models.ForeignKey(settings.AUTH_USER_MODEL,\
                            on_delete=models.CASCADE,\
                            null=False,\
                            blank=USER_BLANK)

    last_modified = models.DateTimeField(auto_now=True)

    time_created = models.DateTimeField(auto_now_add=True)

models.signals.post_delete.connect(Base.post_delete_delete_file_fields)

### Dataset ###

class Dataset(Base):

    name_singular = "Dataset"
    name_plural = "Datasets"

    def __str__(self):
        return str(self.title)

    def read_df_file(self):
        return read_csv(self.df_file)

    def make_df_file(df, title):
        s_buf = io.StringIO()
        df.to_csv(s_buf, index=False)
        return File(s_buf, title)

    def user_directory_path(instance, filename):
        # files will be uploaded to MEDIA_ROOT/user_<id>/{key}s/<filename>
        return "user_{0}/{1}s/{2}".format(instance.user.id, instance.key, filename)

    def get_num_rows(df):
        return len(df.index)

    def get_num_columns(df):
        return len(df.columns)

    def get_creator(self):
        if hasattr(self, 'datasetupload'):
            return self.datasetupload
        elif hasattr(self, 'predictionordinaryleastsquaress_as_y'):
            return self.predictionordinaryleastsquaress_as_y
        elif hasattr(self, 'predictionridgeregressions_as_y'):
            return self.predictionridgeregressions_as_y

    ### num_rows ###
    NUM_ROWS_NULL = True
    NUM_ROWS_BLANK = True
    num_rows = models.PositiveIntegerField(null=NUM_ROWS_NULL,\
                                        blank=NUM_ROWS_BLANK)

    ### num_columns ###
    NUM_COLUMNS_NULL = True
    NUM_COLUMNS_BLANK = True
    num_columns = models.PositiveIntegerField(null=NUM_COLUMNS_NULL,\
                                            blank=NUM_COLUMNS_BLANK)

    ### df_file ###
    df_file = models.FilePathField(path=settings.MEDIA_ROOT)

    ### title ###
    MAX_LENGTH_TITLE = 50
    BLANK_TITLE = True
    NULL_TITLE = False
    title = models.CharField(max_length=MAX_LENGTH_TITLE,
                            null=NULL_TITLE,
                            blank=BLANK_TITLE)

### Uploads ###

class DatasetUpload(Base):

    name_singular = "Dataset Upload"
    name_plural = "Dataset Uploads"

    def __str__(self):
        return str(self.title)
        
    @staticmethod
    def post_save_updates(sender, instance, **kwargs):
        # Ensure dependent components are shown as potentially old versions
        instance.dataset.updated = False
        # Ensure path to file is updated on dataset
        instance.dataset.df_file = instance.df_file.path
        instance.dataset.save()

    def read_uploaded_file(df_file):
        if isinstance(df_file, InMemoryUploadedFile) or isinstance(df_file, File):
            df = read_csv(df_file)
        else:
            df = read_csv(str(df_file))
        return df

    ### title ###
    MAX_LENGTH_TITLE = 50
    BLANK_TITLE = True
    NULL_TITLE = False
    HELP_TEXT_TITLE = "The title for the dataset. Defaults to the filename, with the extension."
    title = models.CharField(max_length=MAX_LENGTH_TITLE,
                            null=NULL_TITLE,
                            blank=BLANK_TITLE,
                            help_text=HELP_TEXT_TITLE)

    ### df_file ###
    BLANK_DF_FILE = False
    UPLOAD_TO_DF_FILE = Dataset.user_directory_path
    df_file = models.FileField(blank=BLANK_DF_FILE,
                                upload_to=UPLOAD_TO_DF_FILE)

    ### dataset ###
    RELATED_NAME_DATASET = '%(class)s'
    dataset = models.OneToOneField(Dataset,\
                                    on_delete=models.CASCADE,\
                                    blank=True,\
                                    related_name=RELATED_NAME_DATASET)

models.signals.post_save.connect(DatasetUpload.post_save_updates, sender=DatasetUpload)

### Prediction ###

class PredictionXYAbstract(Base):

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.title)
        
    @staticmethod
    def post_save_updates(sender, instance, **kwargs):
        # Ensure path to file is updated on dataset
        instance.y.df_file = instance.y_file.path
        instance.y.save()

    ### title ###
    MAX_LENGTH_TITLE = 50
    BLANK_TITLE = True
    NULL_TITLE = False
    DEFAULT_TITLE = "Prediction"
    HELP_TEXT_TITLE = "The title for the predicted dataset."
    title = models.CharField(max_length=MAX_LENGTH_TITLE,
                            null=NULL_TITLE,
                            blank=BLANK_TITLE,
                            default=DEFAULT_TITLE,
                            help_text=HELP_TEXT_TITLE)

    ### x ###
    NULL_X = True
    ON_DELETE_X = models.CASCADE
    RELATED_NAME_X = '%(class)ss_as_x'
    HELP_TEXT_X = "The data to input to the regression for prediction."
    x = models.ForeignKey(Dataset,
                        null=NULL_X,
                        on_delete=ON_DELETE_X,
                        related_name=RELATED_NAME_X,
                        help_text=HELP_TEXT_X)

    ### y ###
    NULL_Y = True
    BLANK_Y = True
    ON_DELETE_Y = models.CASCADE
    RELATED_NAME_Y = '%(class)ss_as_y'
    y = models.OneToOneField(Dataset,
                        null=NULL_Y,
                        blank=BLANK_Y,
                        on_delete=ON_DELETE_Y,
                        related_name=RELATED_NAME_Y)

    ### y_file ###
    BLANK_Y_FILE = True
    UPLOAD_TO_Y_FILE = Dataset.user_directory_path
    y_file = models.FileField(blank=BLANK_Y_FILE,
                                upload_to=UPLOAD_TO_Y_FILE)

class PredictionOrdinaryLeastSquares(PredictionXYAbstract):

    name_singular = "Prediction - Ordinary Least Squares"
    name_plural = "Predictions - Ordinary Least Squares"

    ### regression ###
    REGRESSION = 'OrdinaryLeastSquares'
    NULL_REGRESSION = True
    ON_DELETE_REGRESSION = models.SET_NULL
    RELATED_NAME_REGRESSION = '%(class)ss'
    regression = models.ForeignKey(REGRESSION,
                        null=NULL_REGRESSION,
                        on_delete=ON_DELETE_REGRESSION,
                        related_name=RELATED_NAME_REGRESSION)

models.signals.post_save.connect(PredictionOrdinaryLeastSquares.post_save_updates, sender=PredictionOrdinaryLeastSquares)

class PredictionRidgeRegression(PredictionXYAbstract):

    name_singular = "Prediction - Ridge Regression"
    name_plural = "Predictions - Ridge Regressions"

    REGRESSION = 'RidgeRegression'
    NULL_REGRESSION = True
    ON_DELETE_REGRESSION = models.SET_NULL
    RELATED_NAME_REGRESSION = '%(class)ss'
    regression = models.ForeignKey(REGRESSION,
                                null=NULL_REGRESSION,
                                on_delete=ON_DELETE_REGRESSION,
                                related_name=RELATED_NAME_REGRESSION)

models.signals.post_save.connect(PredictionRidgeRegression.post_save_updates, sender=PredictionRidgeRegression)

### Regression ###

class RegressionXYAbstract(Base):

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.title)

    def refresh(self):
        reg = self.fit_reg()
        self.reg_file = __class__.pickle_reg(reg, self.title)
        self.save()

    @classmethod
    def static_fit_reg(cls, *args, **kwargs):
        reg = cls.get_regression_cls()
        reg = reg()
        reg.fit(*args, **kwargs)
        return reg

    def fit_reg(self):
        reg = self.regression_cls()
        reg = reg()
        reg.fit(self.x.read_df_file(),
                self.y.read_df_file())
        return reg

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/{key}s/<filename>
        return 'user_{0}/{1}s/{2}'.format(instance.user.id, instance.key, filename)

    def pickle_reg(reg, title):
        return File(io.BytesIO(pickle.dumps(reg)), name=title)

    def open_reg(self):
        with open(self.reg_file.path, 'rb') as file:
            return pickle.load(file)

    def pred(self, x):
        header = self.y.read_df_file().columns
        y = self.open_reg().predict(x)
        y = DataFrame(data=y, columns=header)
        return y

    ### title ###
    MAX_LENGTH_TITLE = 20
    BLANK_TITLE = False
    HELP_TEXT_TITLE = "Title for the regression."
    title = models.CharField(max_length=MAX_LENGTH_TITLE,\
                            blank=BLANK_TITLE)

    ### x ###
    NULL_X = True
    ON_DELETE_X = models.CASCADE
    RELATED_NAME_X = '%(class)ss_as_x'
    HELP_TEXT_X = "The input/X dataset to fit the regression."
    x = models.ForeignKey(Dataset,
                        null=NULL_X,
                        on_delete=ON_DELETE_X,
                        related_name=RELATED_NAME_X)

    ### y ###
    NULL_Y = True
    ON_DELETE_Y = models.CASCADE
    RELATED_NAME_Y = '%(class)ss_as_y'
    HELP_TEXT_Y = "The output/observations/Y dataset to fit the regression."
    y = models.ForeignKey(Dataset,
                        null=NULL_Y,
                        on_delete=ON_DELETE_Y,
                        related_name=RELATED_NAME_Y)

    ### reg_file ###
    UPLOAD_TO_REG_FILE = user_directory_path
    NULL_REG_FILE = True
    BLANK_REG_FILE = True
    reg_file = models.FileField(upload_to=UPLOAD_TO_REG_FILE,\
                                null=NULL_REG_FILE,
                                blank=BLANK_REG_FILE)

class OrdinaryLeastSquares(RegressionXYAbstract):

    name_singular = "Ordinary Least Squares"
    name_plural = "Ordinary Least Squares"

    def get_regression_cls():
        return LinearRegression

class RidgeRegression(RegressionXYAbstract):

    name_singular = "Ridge Regression"
    name_plural = "Ridge Regressions"

    def get_regression_cls():
        return Ridge

    @classmethod
    def static_fit_reg(cls, x, y, **kwargs):
        reg = cls.get_regression_cls()
        reg = reg(**kwargs)
        reg.fit(x, y)
        return reg

    def fit_reg(self):
        reg = RidgeRegression.get_regression_cls()
        reg = reg(alpha=self.alpha, solver=self.solver)
        reg.fit(self.x.read_df_file(),
                self.y.read_df_file())
        return reg

    ### alpha ###
    BLANK_ALPHA = False
    NULL_ALPHA = False
    DEFAULT_ALPHA = 1
    HELP_TEXT_ALPHA = "Constant that multiplies the L2 term, controlling regularization strength. alpha must be a non-negative float i.e. in [0, inf)."
    alpha = models.FloatField(blank=BLANK_ALPHA,
                            null=NULL_ALPHA,
                            default=DEFAULT_ALPHA,
                            validators=[MinValueValidator(0)],
                            help_text=HELP_TEXT_ALPHA)

    ### solver ###
    CHOICES_SOLVER = [('auto', "auto"),
                        ('svd', "svd"),
                        ('cholesky', "cholesky"),
                        ('lsqr', "lsqr"),
                        ('sparse_cg', "sparse_cg"),
                        ('sag', "sag"),
                        ('saga', "saga"),
                        ('lbfgs', "lbfgs"),
                    ]
    MAX_LENGTH_SOLVER = max_length(CHOICES_SOLVER)
    DEFAULT_SOLVER = 'auto'
    NULL_SOLVER = False
    BLANK_SOLVER = False
    HELP_TEXT_SOLVER = "Solver to use in the computational routines."
    solver = models.CharField(choices=CHOICES_SOLVER,\
                                max_length=MAX_LENGTH_SOLVER,\
                                default=DEFAULT_SOLVER,\
                                null=NULL_SOLVER,\
                                blank=BLANK_SOLVER,\
                                help_text=HELP_TEXT_SOLVER)

### Visualization ###

class VisualizationXAbstract(Base):

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.title)

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/{key}s/<filename>
        return "user_{0}/{1}s/{2}".format(instance.user.id, instance.key, filename)

    def refresh(self):
        self.x.df = self.x.read_df_file() # Ensure x data has been read up to date
        self.plot() # Plot the data
        self.pickle_fig() # Pickle the figure
        self.save() # Save model

    def plot(self):
        pass

    @classmethod
    def static_plot(cls, *args, **kwargs):
        fig = cls.get_plot_cls()
        fig = fig(*args, **kwargs)
        return fig

    def pickle_fig(self):
        self.fig_file = __class__.static_pickle_fig(self.fig, self.title)

    @staticmethod
    def static_pickle_fig(fig, title):
        return File(io.BytesIO(pickle.dumps(fig)), name=title)

    def open_fig(self):
        with open(self.fig_file.path, 'rb') as file:
            return pickle.load(file)

    ### title ###
    MAX_LENGTH_TITLE = 20
    HELP_TEXT_TITLE = "The title of the visualization."
    title = models.CharField(max_length=MAX_LENGTH_TITLE,\
                            blank=False,
                            help_text=HELP_TEXT_TITLE)

    ### x ###
    HELP_TEXT_X = "The data to visualize."
    x = models.ForeignKey('Dataset',
                        null=True,
                        on_delete=models.CASCADE,
                        related_name='%(class)ss',
                        help_text=HELP_TEXT_X)

    ### fig_file ###
    BLANK_FIG_FILE = True
    NULL_FIG_FILE = False
    fig_file = models.FileField(upload_to=user_directory_path,\
                                blank=BLANK_FIG_FILE,\
                                null=NULL_FIG_FILE)

class ScatterMatrix(VisualizationXAbstract):

    name_singular = "Scatter Matrix"
    name_plural = "Scatter Matrices"

    def get_plot_cls():
        return px.scatter_matrix

    def plot(self):
        self.fig = self.static_plot(self.x.df,
                                title=self.title)

class Histogram(VisualizationXAbstract):

    name_singular = "Histogram"
    name_plural = "Histograms"

    def get_plot_cls():
        return px.histogram

    def plot(self):
        self.fig = self.static_plot(self.x.df,
                                title=self.title,
                                nbins=self.nbins)

    ### nbins ###
    BLANK_NBINS = True
    NULL_NBINS = True
    HELP_TEXT_NBINS = "The number of bins to use."
    nbins = models.PositiveIntegerField(blank=BLANK_NBINS,
                                        null=NULL_NBINS,
                                        help_text=HELP_TEXT_NBINS)

### Workspace ###

class Workspace(Base):

    name_singular = "Workspace"
    name_plural = "Workspaces"

    def __str__(self):
        return str(self.title)

    ### title ###
    MAX_LENGTH_TITLE = 20
    DEFAULT_TITLE = "Workspace"
    HELP_TEXT_TITLE = "The title of the workspace."
    title = models.CharField(max_length=MAX_LENGTH_TITLE,\
                            blank=False,
                            default=DEFAULT_TITLE,
                            help_text=HELP_TEXT_TITLE)

    ### datasets ###
    datasets = models.ManyToManyField('Dataset', related_name='%(class)ss')

    datasetuploads = models.ManyToManyField('DatasetUpload', related_name='%(class)ss')
    predictionordinaryleastsquaress = models.ManyToManyField('PredictionOrdinaryLeastSquares', related_name='%(class)ss')
    predictionridgeregressions = models.ManyToManyField('PredictionRidgeRegression', related_name='%(class)ss')

    ### regressions ###
    ordinaryleastsquaress = models.ManyToManyField('OrdinaryLeastSquares', related_name='%(class)ss')
    ridgeregressions = models.ManyToManyField('RidgeRegression', related_name='%(class)ss')

    ### visualizations ###
    scattermatrixs = models.ManyToManyField('ScatterMatrix', related_name='%(class)ss')
    histograms = models.ManyToManyField('Histogram', related_name='%(class)ss')
