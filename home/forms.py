from django import forms
from django.core.exceptions import ValidationError
import pickle
import io
from django.core.files import File
from .models import to_dict, \
                    Workspace,\
                    Dataset, DatasetUpload,\
                    OrdinaryLeastSquares, PredictionOrdinaryLeastSquares,\
                    RidgeRegression, PredictionRidgeRegression,\
                    ScatterMatrix,\
                    Histogram
from account.models import CustomUser

### Workspace ###

class SelectWorkspaceForm(forms.Form):

    workspace = forms.ModelChoiceField(queryset=Workspace.objects.none())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SelectWorkspaceForm, self).__init__(*args, **kwargs)
        self.fields['workspace'].queryset = Workspace.objects.filter(user=self.user)

    def clean_workspace(self):
        workspace = self.cleaned_data.get('workspace')
        if workspace.user != self.user:
            message = "This is not your workspace!"
            raise ValidationError(message, code='invalid_user')
        return workspace

class DeleteWorkspaceForm(SelectWorkspaceForm):
    pass

class CreateWorkspaceForm(forms.ModelForm):

    class Meta:
        model = Workspace
        fields = ['title', 'user']
        widgets = {'user':forms.HiddenInput()}

class UpdateWorkspaceForm(CreateWorkspaceForm):
    
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['workspace'].queryset = Workspace.objects.filter(user=self.user)

### Generalized component ###

class SelectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)

class CreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)

class CreatePredictionRegressionXYForm(CreateForm):

    class Meta:
        fields = ['user', 'title', 'regression', 'x', 'y', 'y_file']
        widgets = {'user':forms.HiddenInput(),
                'regression':forms.HiddenInput(),
                'y':forms.HiddenInput(),
                'y_file':forms.HiddenInput()}

    def make_y_dataset(self, y_df):
        return Dataset(user=self.user,\
                    num_rows=Dataset.get_num_rows(y_df),
                    num_columns=Dataset.get_num_columns(y_df),\
                    title=self.cleaned_data.get('title'))

    def clean(self):
        title = self.cleaned_data.get('title')
        x = self.cleaned_data.get('x')
        regression = self.cleaned_data.get('regression')
        if x is None or regression is None: # Can't do further processing, raise existing errors
            return self.cleaned_data
        
        x = x.read_df_file()
        y_df = regression.pred(x)
        y_file = Dataset.make_df_file(y_df, title+'.csv')

        y = self.make_y_dataset(y_df)
        self.cleaned_data['y_file'] = y_file
        self.cleaned_data['y'] = y

        return self.cleaned_data

class UpdatePredictionRegressionXYForm(CreatePredictionRegressionXYForm):

    def make_y_dataset(self, y_df):
        dataset = self.cleaned_data.get(self.Meta.model().key).y
        dataset.num_rows = Dataset.get_num_rows(y_df)
        dataset.num_columns = Dataset.get_num_columns(y_df)
        dataset.title = self.cleaned_data.get('title')
        return dataset

class DuplicatePredictionRegressionXYForm(UpdatePredictionRegressionXYForm):
    pass

class CreateRegressionXYForm(CreateForm):

    class Meta:
        fields = ['user', 'title', 'x', 'y', 'reg_file']
        widgets = {'user':forms.HiddenInput(), 'reg_file':forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)
        self.fields['y'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)

    def read_in_xy(self):
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        if x is None or y is None: # Can't do further processing, raise existing errors
            return self.cleaned_data

        x_dataset = x.read_df_file()
        y_dataset = y.read_df_file()
        
        if Dataset.get_num_rows(x_dataset) != Dataset.get_num_rows(y_dataset):
            message = "The number of x samples must equal the number of y samples."
            raise ValidationError(message, code='unequal_samples') 
        
        return x_dataset, y_dataset

    def clean(self):
        title = self.cleaned_data.get('title')
        x_dataset, y_dataset = self.read_in_xy()

        reg = self.Meta.model.static_fit_reg(x_dataset, y_dataset)
        reg_file = self.Meta.model.pickle_reg(reg, title)
        self.cleaned_data['reg_file'] = reg_file

        return self.cleaned_data

class UpdateRegressionXYForm(CreateRegressionXYForm):
    pass

class DuplicateRegressionXYForm(UpdateRegressionXYForm):
    pass

class CreateVisualizationXForm(CreateForm):

    class Meta:
        fields = ['user', 'title', 'x', 'fig_file']
        widgets = {'user':forms.HiddenInput(), 'fig_file':forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)
       
    def clean(self):
        title = self.cleaned_data.get('title')
        x = self.cleaned_data.get('x')
        if x is None: # Can't do further processing, raise existing errors
            return self.cleaned_data
    
        x_dataset = x.read_df_file()
        fig = self.Meta.model.static_plot(x_dataset,
                                        title=title)
        fig_file = self.Meta.model.static_pickle_fig(fig, title)
        self.cleaned_data['fig_file'] = fig_file

        return self.cleaned_data

class UpdateVisualizationXForm(CreateVisualizationXForm):
    pass

class DuplicateVisualizationXForm(UpdateVisualizationXForm):
    pass

### Dataset Upload ###

class SelectDatasetUploadForm(SelectForm):

    datasetupload = forms.ModelChoiceField(queryset=DatasetUpload.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['datasetupload'].queryset = DatasetUpload.objects.filter(user=self.user, workspaces=self.workspace)

class DeleteDatasetUploadForm(SelectDatasetUploadForm):
    pass

class CreateDatasetUploadForm(CreateForm):

    class Meta:
        model = DatasetUpload
        fields = ['df_file', 'title', 'dataset']
        widgets = {'dataset':forms.HiddenInput()}

    def clean(self):
        df_file = self.cleaned_data.get('df_file')
        if df_file is None: # Can't do further processing, raise existing errors
            return self.cleaned_data
        df = DatasetUpload.read_uploaded_file(df_file)
        num_rows = Dataset.get_num_rows(df)
        num_columns = Dataset.get_num_columns(df)
        title = self.cleaned_data.get('title')
        if title == '':
            title = str(self.cleaned_data.get('df_file'))
        dataset = Dataset(num_rows=num_rows,
                        num_columns=num_columns,\
                        title=title)
        self.cleaned_data['title'] = title
        self.cleaned_data['dataset'] = dataset
        return self.cleaned_data

class UpdateDatasetUploadForm(CreateDatasetUploadForm):

    datasetupload = forms.ModelChoiceField(queryset=DatasetUpload.objects.none(), widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(UpdateDatasetUploadForm, self).__init__(*args, **kwargs)
        self.fields['dataset'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)
        self.fields['dataset'].widget = forms.HiddenInput()
        self.fields['datasetupload'].queryset = DatasetUpload.objects.filter(user=self.user, workspaces=self.workspace)
        self.fields['df_file'].required = False # Not required, can just re-use old DatasetUpload.df_file to avoid user needing to search their file system

    def clean(self):
        # If no new file is uploaded, reference the existing file from the old datasetupload entry
        df_file = self.cleaned_data.get('df_file')
        if not df_file:
            datasetupload = self.cleaned_data.get('datasetupload')
            self.cleaned_data['df_file'] = datasetupload.df_file

        dataset_old = self.cleaned_data.get('dataset')
        self.cleaned_data = super().clean()
        dataset_new = self.cleaned_data.get('dataset')
        dataset_old.num_rows = dataset_new.num_rows
        dataset_old.num_columns = dataset_new.num_columns
        dataset_old.title = dataset_new.title
        self.cleaned_data['dataset'] = dataset_old

        return self.cleaned_data

class DuplicateDatasetUploadForm(UpdateDatasetUploadForm):
    pass

### PredictionOrdinaryLeastSquares ###

class SelectPredictionOrdinaryLeastSquaresForm(SelectForm):

    predictionordinaryleastsquares = forms.ModelChoiceField(queryset=PredictionOrdinaryLeastSquares.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['predictionordinaryleastsquares'].queryset = PredictionOrdinaryLeastSquares.objects.filter(user=self.user, workspaces=self.workspace)

class DeletePredictionOrdinaryLeastSquaresForm(SelectPredictionOrdinaryLeastSquaresForm):
    pass

class CreatePredictionOrdinaryLeastSquaresForm(CreatePredictionRegressionXYForm):

    class Meta(CreatePredictionRegressionXYForm.Meta):
        model = PredictionOrdinaryLeastSquares
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)
        self.fields['regression'].queryset = OrdinaryLeastSquares.objects.filter(user=self.user, workspaces=self.workspace)

class UpdatePredictionOrdinaryLeastSquaresForm(CreatePredictionOrdinaryLeastSquaresForm, UpdatePredictionRegressionXYForm):

    predictionordinaryleastsquares = forms.ModelChoiceField(queryset=PredictionOrdinaryLeastSquares.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['predictionordinaryleastsquares'].queryset = PredictionOrdinaryLeastSquares.objects.filter(user=self.user, workspaces=self.workspace)

class DuplicatePredictionOrdinaryLeastSquaresForm(UpdatePredictionOrdinaryLeastSquaresForm, DuplicatePredictionRegressionXYForm):
    pass

### PredictionRidgeRegression ###

class SelectPredictionRidgeRegressionForm(SelectForm):

    predictionridgeregression = forms.ModelChoiceField(queryset=PredictionRidgeRegression.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['predictionridgeregression'].queryset = PredictionRidgeRegression.objects.filter(user=self.user, workspaces=self.workspace)

class DeletePredictionRidgeRegressionForm(SelectPredictionRidgeRegressionForm):
    pass

class CreatePredictionRidgeRegressionForm(CreatePredictionRegressionXYForm):

    class Meta(CreatePredictionRegressionXYForm.Meta):
        model = PredictionRidgeRegression

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x'].queryset = Dataset.objects.filter(user=self.user, workspaces=self.workspace)
        self.fields['regression'].queryset = RidgeRegression.objects.filter(user=self.user, workspaces=self.workspace)

class UpdatePredictionRidgeRegressionForm(CreatePredictionRidgeRegressionForm, UpdatePredictionRegressionXYForm):

    predictionridgeregression = forms.ModelChoiceField(queryset=PredictionRidgeRegression.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['predictionridgeregression'].queryset = PredictionRidgeRegression.objects.filter(user=self.user, workspaces=self.workspace)

class DuplicatePredictionRidgeRegressionForm(UpdatePredictionRidgeRegressionForm, DuplicatePredictionRegressionXYForm):
    pass

### OrdinaryLeastSquares ###

class SelectOrdinaryLeastSquaresForm(SelectForm):

    ordinaryleastsquares = forms.ModelChoiceField(queryset=OrdinaryLeastSquares.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordinaryleastsquares'].queryset = OrdinaryLeastSquares.objects.filter(user=self.user, workspaces=self.workspace)

class DeleteOrdinaryLeastSquaresForm(SelectOrdinaryLeastSquaresForm):
    pass

class CreateOrdinaryLeastSquaresForm(CreateRegressionXYForm):

    class Meta(CreateRegressionXYForm.Meta):
        model = OrdinaryLeastSquares

class UpdateOrdinaryLeastSquaresForm(CreateOrdinaryLeastSquaresForm, UpdateRegressionXYForm):

    ordinaryleastsquares = forms.ModelChoiceField(queryset=OrdinaryLeastSquares.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordinaryleastsquares'].queryset = OrdinaryLeastSquares.objects.filter(user=self.user, workspaces=self.workspace)

class DuplicateOrdinaryLeastSquaresForm(UpdateOrdinaryLeastSquaresForm, DuplicateRegressionXYForm):
    pass

### RidgeRegression ###

class SelectRidgeRegressionForm(SelectForm):

    ridgeregression = forms.ModelChoiceField(queryset=RidgeRegression.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ridgeregression'].queryset = RidgeRegression.objects.filter(user=self.user, workspaces=self.workspace)

class DeleteRidgeRegressionForm(SelectRidgeRegressionForm):
    pass

class CreateRidgeRegressionForm(CreateRegressionXYForm):

    class Meta(CreateRegressionXYForm.Meta):
        model = RidgeRegression
        fields = ['user', 'title', 'x', 'y', 'alpha', 'solver', 'reg_file']

    def clean(self):
        title = self.cleaned_data.get('title')
        x_dataset, y_dataset = self.read_in_xy()
        alpha = self.cleaned_data.get('alpha')
        solver = self.cleaned_data.get('solver')

        reg = self.Meta.model.static_fit_reg(x_dataset, y_dataset, alpha=alpha, solver=solver)
        reg_file = self.Meta.model.pickle_reg(reg, title)
        self.cleaned_data['reg_file'] = reg_file

        return self.cleaned_data

class UpdateRidgeRegressionForm(CreateRidgeRegressionForm, UpdateRegressionXYForm):

    ridgeregression = forms.ModelChoiceField(queryset=RidgeRegression.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ridgeregression'].queryset = RidgeRegression.objects.filter(user=self.user, workspaces=self.workspace)

    def clean(self):
        return CreateRidgeRegressionForm.clean(self)

class DuplicateRidgeRegressionForm(UpdateRidgeRegressionForm, DuplicateRegressionXYForm):
    pass

### ScatterMatrix ###

class SelectScatterMatrixForm(SelectForm):

    scattermatrix = forms.ModelChoiceField(queryset=ScatterMatrix.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scattermatrix'].queryset = ScatterMatrix.objects.filter(user=self.user, workspaces=self.workspace)

class DeleteScatterMatrixForm(SelectScatterMatrixForm):
    pass

class CreateScatterMatrixForm(CreateVisualizationXForm):

    class Meta(CreateVisualizationXForm.Meta):
        model = ScatterMatrix

class UpdateScatterMatrixForm(CreateScatterMatrixForm, UpdateVisualizationXForm):
    
    scattermatrix = forms.ModelChoiceField(queryset=ScatterMatrix.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scattermatrix'].queryset = ScatterMatrix.objects.filter(user=self.user, workspaces=self.workspace)

class DuplicateScatterMatrixForm(UpdateScatterMatrixForm, DuplicateVisualizationXForm):
    pass

### Histogram ###

class SelectHistogramForm(SelectForm):

    histogram = forms.ModelChoiceField(queryset=Histogram.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['histogram'].queryset = Histogram.objects.filter(user=self.user, workspaces=self.workspace)

class DeleteHistogramForm(SelectHistogramForm):
    pass

class CreateHistogramForm(CreateVisualizationXForm):

    class Meta(CreateVisualizationXForm.Meta):
        model = Histogram
        fields = ['user', 'title', 'x', 'nbins', 'fig_file']

    def clean(self):
        title = self.cleaned_data.get('title')
        nbins = self.cleaned_data.get('nbins')
        x = self.cleaned_data.get('x')
        if x is None: # Can't do further processing, raise existing errors
            return self.cleaned_data

        x_dataset = x.read_df_file()
        fig = Histogram.static_plot(x_dataset,
                                    title=title,
                                    nbins=nbins)
        fig_file = Histogram.static_pickle_fig(fig, title)
        self.cleaned_data['fig_file'] = fig_file

        return self.cleaned_data

class UpdateHistogramForm(CreateHistogramForm, UpdateVisualizationXForm):
    
    histogram = forms.ModelChoiceField(queryset=Histogram.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['histogram'].queryset = Histogram.objects.filter(user=self.user, workspaces=self.workspace)

class DuplicateHistogramForm(UpdateHistogramForm, DuplicateVisualizationXForm):
    pass
