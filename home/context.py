from .models import Workspace,\
                    Dataset, DatasetUpload,\
                    OrdinaryLeastSquares, PredictionOrdinaryLeastSquares,\
                    RidgeRegression, PredictionRidgeRegression,\
                    ScatterMatrix, Histogram
from .forms import CreateWorkspaceForm, SelectWorkspaceForm, DeleteWorkspaceForm,\
                    CreateDatasetUploadForm, UpdateDatasetUploadForm, DuplicateDatasetUploadForm,\
                    CreatePredictionOrdinaryLeastSquaresForm, UpdatePredictionOrdinaryLeastSquaresForm, DuplicatePredictionOrdinaryLeastSquaresForm,\
                    CreatePredictionRidgeRegressionForm, UpdatePredictionRidgeRegressionForm, DuplicatePredictionRidgeRegressionForm,\
                    CreateOrdinaryLeastSquaresForm, UpdateOrdinaryLeastSquaresForm, DuplicateOrdinaryLeastSquaresForm,\
                    CreateRidgeRegressionForm, UpdateRidgeRegressionForm, DuplicateRidgeRegressionForm,\
                    CreateScatterMatrixForm, UpdateScatterMatrixForm, DuplicateScatterMatrixForm,\
                    CreateHistogramForm, UpdateHistogramForm, DuplicateHistogramForm

##### Context by page section #####

class MenuContext():
    
    def get_menu_context(request, user):

        workspaces = Workspace.objects.filter(user=user)

        context = {}

        context['workspaces'] = workspaces
        context['create_workspace_form'] = CreateWorkspaceForm
        context['select_workspace_form'] = SelectWorkspaceForm(user=user)
        context['delete_workspace_form'] = DeleteWorkspaceForm(user=user)
        context['Workspace'] = Workspace()

        context['Dataset'] = Dataset()

        context['create_datasetupload_form'] = CreateDatasetUploadForm
        context['DatasetUpload'] = DatasetUpload()

        context['create_ordinaryleastsquares_form'] = CreateOrdinaryLeastSquaresForm
        context['OrdinaryLeastSquares'] = OrdinaryLeastSquares()
        context['create_ridgeregression_form'] = CreateRidgeRegressionForm
        context['RidgeRegression'] = RidgeRegression()

        context['create_scattermatrix_form'] = CreateScatterMatrixForm
        context['ScatterMatrix'] = ScatterMatrix()
        context['create_histogram_form'] = CreateHistogramForm
        context['Histogram'] = Histogram()
        
        return context

class WorkspaceContext():

    def get_workspace_active(request):
        workspace_active_id = request.session.get('workspace_active', None)
        if workspace_active_id:
            return Workspace.objects.get(user=request.user, id=workspace_active_id)
        return None

    def get_or_create_workspace_active(request):
        workspace_active = WorkspaceContext.get_workspace_active(request)
        if workspace_active:
            return workspace_active
        else:
            workspace_active = Workspace(user=request.user)
            workspace_active.save()
            request.session['workspace_active'] = workspace_active.id
        return workspace_active

    def get_workspace_context(request, user):

        context = {}

        workspace_active = WorkspaceContext.get_workspace_active(request)

        if workspace_active:
            context['workspace_active'] = workspace_active
            context['select_workspace_form'] = SelectWorkspaceForm(initial={'workspace':workspace_active}, user=user)

            context['create_ordinaryleastsquares_form'] = CreateOrdinaryLeastSquaresForm(user=user, workspace=workspace_active)
            context['create_ridgeregression_form'] = CreateRidgeRegressionForm(user=user, workspace=workspace_active)

            context['create_scattermatrix_form'] = CreateScatterMatrixForm(user=user, workspace=workspace_active)
            context['create_histogram_form'] = CreateHistogramForm(user=user, workspace=workspace_active)

            context['datasets'] = {'datasetuploads': [GetDatasetUploadContext(datasetupload, workspace=workspace_active).get_context() 
                                    for datasetupload in workspace_active.datasetuploads.all()],
                                    'predictionordinaryleastsquaress': [GetPredictionOrdinaryLeastSquaresContext(predictionordinaryleastsquares, workspace=workspace_active).get_context() 
                                    for predictionordinaryleastsquares in workspace_active.predictionordinaryleastsquaress.all()],
                                    'predictionridgeregressions': [GetPredictionRidgeRegressionContext(predictionridgeregression, workspace=workspace_active).get_context() 
                                    for predictionridgeregression in workspace_active.predictionridgeregressions.all()]
            }

            context['ordinaryleastsquaress'] = [GetOrdinaryLeastSquaresContext(ordinaryleastsquares, workspace=workspace_active)
                                                    .get_context() 
                                                        for ordinaryleastsquares in workspace_active.ordinaryleastsquaress.all()]
            context['ridgeregressions'] = [GetRidgeRegressionContext(ridgeregression, workspace=workspace_active)
                                                    .get_context() 
                                                        for ridgeregression in workspace_active.ridgeregressions.all()]

            context['scattermatrixs'] = [GetScatterMatrixContext(scattermatrix, workspace=workspace_active)
                                                    .get_context() 
                                                        for scattermatrix in workspace_active.scattermatrixs.all()]
            context['histograms'] = [GetHistogramContext(histogram, workspace=workspace_active)
                                                    .get_context() 
                                                        for histogram in workspace_active.histograms.all()]

        return context

class HomeContext(MenuContext, WorkspaceContext):

    def get_home_context(request):

        user = None
        if request.user.is_authenticated:
            user = request.user

        context = {**HomeContext.get_menu_context(request, user), **HomeContext.get_workspace_context(request, user)}

        return context

###### Context by component ######

class GetComponentContext:

    def __init__(self, *args, **kwargs):

        self.component = args[0]
        self.workspace = kwargs.get('workspace')
        self.creator = self.component.get_creator() if hasattr(self.component, 'get_creator') else self.component
        
        self.create_form = kwargs.get('create_form', None)
        self.update_form = kwargs.get('update_form', None)
        self.duplicate_form = kwargs.get('duplicate_form', None)

        self.create_form_template = kwargs.get('create_form_template', 'home/create_'+self.creator.key+'.html')
        self.update_form_template = kwargs.get('update_form_template', 'home/update_'+self.creator.key+'.html')
        self.duplicate_form_template = kwargs.get('duplicate_form_template', 'home/duplicate_'+self.creator.key+'.html')

    def get_context(self):
        self.initialize_create_form()
        self.initialize_update_form()
        self.initialize_duplicate_form()
        return {self.component.key:self.component,
                'creator':self.creator, 
                'create_form':self.create_form,
                'create_form_template':self.create_form_template,
                'update_form':self.update_form,
                'update_form_template':self.update_form_template,
                'duplicate_form':self.duplicate_form,
                'duplicate_form_template':self.duplicate_form_template}

    def determine_create_form(self):
        pass

    def determine_update_form(self):
        pass

    def determine_duplicate_form(self):
        pass

    def initialize_create_form(self):
        if self.create_form is None:
            self.determine_create_form()
        self.create_form = self.create_form(instance=self.creator)

    def initialize_update_form(self):
        if self.update_form is None:
            self.determine_update_form()
        self.update_form = self.update_form(initial={self.creator.key:self.creator.id}, instance=self.creator, user=self.component.user, workspace=self.workspace)

    def initialize_duplicate_form(self):
        if self.duplicate_form is None:
            self.determine_duplicate_form()
        self.duplicate_form = self.duplicate_form(initial={self.creator.key:self.creator.id}, instance=self.creator, user=self.component.user, workspace=self.workspace)

### Datasets ###

class GetDatasetUploadContext(GetComponentContext):

    def determine_create_form(self):
        self.create_form = CreateDatasetUploadForm

    def determine_update_form(self):
        self.update_form = UpdateDatasetUploadForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicateDatasetUploadForm

    def is_updated(self, context):
        return True

    def get_context(self):
        context = super().get_context()
        context[self.component.key].dataset.df = context[self.component.key].dataset.read_df_file()
        context[self.component.key].updated = self.is_updated(context)
        return context

class GetPredictionRegressionContext(GetComponentContext):

    def initialize_create_form(self):
        if self.create_form is None:
            self.determine_create_form()
        self.create_form = self.create_form(instance=self.component,
                                            user=self.component.user,
                                            workspace=self.workspace)

    def initialize_update_form(self):
        super().initialize_update_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.update_form.initial['y_file'] = None

    def initialize_duplicate_form(self):
        super().initialize_duplicate_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.duplicate_form.initial['y_file'] = None

    def is_updated(self, context):
        return context[self.component.key].last_modified >= context[self.component.key].regression.last_modified

    def get_context(self):
        context = super().get_context()
        context[self.component.key].y.df = context[self.component.key].y.read_df_file()
        context[self.component.key].updated = self.is_updated(context)
        return context

class GetPredictionOrdinaryLeastSquaresContext(GetPredictionRegressionContext):

    def determine_create_form(self):
        self.create_form = CreatePredictionOrdinaryLeastSquaresForm

    def determine_update_form(self):
        self.update_form = UpdatePredictionOrdinaryLeastSquaresForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicatePredictionOrdinaryLeastSquaresForm

class GetPredictionRidgeRegressionContext(GetPredictionRegressionContext):

    def determine_create_form(self):
        self.create_form = CreatePredictionRidgeRegressionForm

    def determine_update_form(self):
        self.update_form = UpdatePredictionRidgeRegressionForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicatePredictionRidgeRegressionForm

### Regressions ###

class GetRegressionXYContext(GetComponentContext):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.prediction_obj = kwargs.get('prediction_obj', None)
        self.create_prediction_form = kwargs.get('create_prediction_form', None)
        self.create_prediction_form_template = kwargs.get('create_prediction_form_template', 'home/create_prediction'+self.component.key+'.html')

    def determine_prediction_obj(self):
        pass

    def determine_create_prediction_form(self):
        pass

    def initialize_update_form(self):
        super().initialize_update_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.update_form.initial['reg_file'] = None

    def initialize_duplicate_form(self):
        super().initialize_duplicate_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.duplicate_form.initial['reg_file'] = None

    def initialize_create_form(self):
        if self.create_form is None:
            self.determine_create_form()
        self.create_form = self.create_form(instance=self.creator,
                                            user=self.component.user,
                                            workspace=self.workspace)

    def initialize_create_prediction_form(self):
        if self.create_prediction_form is None:
            self.determine_create_prediction_form()
        if self.prediction_obj is None:
            self.determine_prediction_obj()
        self.create_prediction_form = self.create_prediction_form(
                                    initial={'regression':self.component}, 
                                    user=self.component.user, 
                                    workspace=self.workspace)
        from django.forms.widgets import HiddenInput
        # No need to show the regression being used, this is already in the regression component
        self.create_prediction_form.fields['regression'].widget = HiddenInput()

    def is_updated(self, context):
        x_is_updated = context[self.component.key].last_modified >= context[self.component.key].x.last_modified
        y_is_updated = context[self.component.key].last_modified >= context[self.component.key].y.last_modified
        return x_is_updated and y_is_updated

    def get_context(self):
        context = super().get_context()

        self.initialize_create_prediction_form()
        context['prediction_obj'] = self.prediction_obj
        context['create_prediction_form'] = self.create_prediction_form
        context['create_prediction_form_template'] = self.create_prediction_form_template

        self.component.reg = self.component.open_reg()
        self.component.x.df = self.component.x.read_df_file()
        self.component.y.df = self.component.y.read_df_file()
        context[self.component.key] = self.component

        context[self.component.key].updated = self.is_updated(context)
        
        return context

class GetOrdinaryLeastSquaresContext(GetRegressionXYContext):

    def determine_create_form(self):
        self.create_form = CreateOrdinaryLeastSquaresForm

    def determine_update_form(self):
        self.update_form = UpdateOrdinaryLeastSquaresForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicateOrdinaryLeastSquaresForm

    def determine_prediction_obj(self):
        self.prediction_obj = PredictionOrdinaryLeastSquares()

    def determine_create_prediction_form(self):
        self.create_prediction_form = CreatePredictionOrdinaryLeastSquaresForm

class GetRidgeRegressionContext(GetRegressionXYContext):

    def determine_create_form(self):
        self.create_form = CreateRidgeRegressionForm

    def determine_update_form(self):
        self.update_form = UpdateRidgeRegressionForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicateRidgeRegressionForm
    
    def determine_prediction_obj(self):
        self.prediction_obj = PredictionRidgeRegression()

    def determine_create_prediction_form(self):
        self.create_prediction_form = CreatePredictionRidgeRegressionForm

### Visualizations ###

class GetVisualizationXContext(GetComponentContext):

    def initialize_create_form(self):
        if self.create_form is None:
            self.determine_create_form()
        self.create_form = self.create_form(instance=self.creator,
                                            user=self.component.user,
                                            workspace=self.workspace)

    def initialize_update_form(self):
        super().initialize_update_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.update_form.initial['fig_file'] = None

    def initialize_duplicate_form(self):
        super().initialize_duplicate_form()
        # Remove to pass validation without needing to include request.FILES in form validation check
        self.duplicate_form.initial['fig_file'] = None

    def get_context(self):
        context = super().get_context()
        visualization = context[self.component.key]
        visualization.fig = visualization.open_fig
        context[self.component.key] = visualization
        context[self.component.key].updated = self.is_updated(context)
        return context

class GetScatterMatrixContext(GetVisualizationXContext):

    def determine_create_form(self):
        self.create_form = CreateScatterMatrixForm

    def determine_update_form(self):
        self.update_form = UpdateScatterMatrixForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicateScatterMatrixForm

    def is_updated(self, context):
        x_is_updated = context[self.component.key].last_modified >= context[self.component.key].x.last_modified
        return x_is_updated

class GetHistogramContext(GetVisualizationXContext):

    def determine_create_form(self):
        self.create_form = CreateHistogramForm

    def determine_update_form(self):
        self.update_form = UpdateHistogramForm

    def determine_duplicate_form(self):
        self.duplicate_form = DuplicateHistogramForm

    def is_updated(self, context):
        x_is_updated = context[self.component.key].last_modified >= context[self.component.key].x.last_modified
        return x_is_updated
