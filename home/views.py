from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.apps import apps
from .context import *
from .models import to_dict,\
                    Workspace,\
                    Dataset, DatasetUpload,\
                    OrdinaryLeastSquares, PredictionOrdinaryLeastSquares,\
                    RidgeRegression, PredictionRidgeRegression,\
                    ScatterMatrix, Histogram
from .forms import CreateWorkspaceForm, SelectWorkspaceForm, DeleteWorkspaceForm,\
                    SelectDatasetUploadForm, DeleteDatasetUploadForm,\
                    CreateDatasetUploadForm, UpdateDatasetUploadForm, DuplicateDatasetUploadForm,\
                    SelectPredictionOrdinaryLeastSquaresForm, DeletePredictionOrdinaryLeastSquaresForm,\
                    CreatePredictionOrdinaryLeastSquaresForm, UpdatePredictionOrdinaryLeastSquaresForm, DuplicatePredictionOrdinaryLeastSquaresForm,\
                    SelectPredictionRidgeRegressionForm, DeletePredictionRidgeRegressionForm,\
                    CreatePredictionRidgeRegressionForm, UpdatePredictionRidgeRegressionForm, DuplicatePredictionRidgeRegressionForm,\
                    SelectOrdinaryLeastSquaresForm, DeleteOrdinaryLeastSquaresForm,\
                    CreateOrdinaryLeastSquaresForm, UpdateOrdinaryLeastSquaresForm, DuplicateOrdinaryLeastSquaresForm,\
                    SelectRidgeRegressionForm, DeleteRidgeRegressionForm,\
                    CreateRidgeRegressionForm, UpdateRidgeRegressionForm, DuplicateRidgeRegressionForm,\
                    SelectScatterMatrixForm, DeleteScatterMatrixForm,\
                    CreateScatterMatrixForm, UpdateScatterMatrixForm, DuplicateScatterMatrixForm,\
                    SelectHistogramForm, DeleteHistogramForm,\
                    CreateHistogramForm, UpdateHistogramForm, DuplicateHistogramForm

### Home ###
def home(request):

    context = HomeContext.get_home_context(request)

    return render(request, 'home/home.html', context)

###### Workspace ######
@login_required(login_url='account-login')
def create_workspace(request):

    form = CreateWorkspaceForm(request.POST)

    if form.is_valid():
        workspace_active = form.save(commit=False)
        workspace_active.user = request.user
        workspace_active.save()
        request.session['workspace_active'] = workspace_active.id
        return redirect('home-home')

    context = {'form': form}
    return render(request, 'home/create_workspace.html', context)

@login_required(login_url='account-login')
def select_workspace(request):

    form = SelectWorkspaceForm(request.POST, user=request.user)

    if form.is_valid():
        workspace_active = form.cleaned_data.get('workspace')
        request.session['workspace_active'] = workspace_active.id
        return redirect('home-home')

    context = get_home_context(request)
    context['select_workspace_form'] = form

    return render(request, 'home/home.html', context)

###### Generalized Component ######
@method_decorator(login_required, name="dispatch")
class CRUDComponent(HomeContext, View):

    crud_type = ''

    def bind_select_form(self, request):
        self.workspace_active = HomeContext.get_or_create_workspace_active(request)
        return self.select_form(request.POST, user=request.user, workspace=self.workspace_active)

    def bind_form(self, request):
        self.workspace_active = HomeContext.get_or_create_workspace_active(request)
        # Update forms will have an existing instance to include
        if hasattr(self, 'instance'):
            return self.form(request.POST, request.FILES, user=request.user, workspace=self.workspace_active, instance=self.instance)
        else:
            return self.form(request.POST, request.FILES, user=request.user, workspace=self.workspace_active)

    def post_process_select_form(self, request):
        self.instance = self.bound_select_form.cleaned_data.get(self.component_cls().key)

    def post_process_form(self, request):
        pass

    def valid_return(self, *args, **kwargs):
        return redirect('home-home')

    def invalid_return(self, request, *args, **kwargs):
        context = {}
        context['form'] = self.bound_form
        context['form_action'] = 'home-'+self.crud_type.lower()+'-'+self.component_cls().key
        return render(request, 'home/crud_form.html', context)

    def post(self, request):

        # For forms with select_form (ex. update forms)
        if hasattr(self, 'select_form'):
            self.bound_select_form = self.bind_select_form(request)
            if self.bound_select_form.is_valid():
                self.post_process_select_form(request)

        self.bound_form = self.bind_form(request)

        if self.bound_form.is_valid():
            self.post_process_form(request)
            return self.valid_return()

        return self.invalid_return(request)

class RefreshComponent(CRUDComponent):

    def bind_select_form(self, request):
        self.workspace_active = HomeContext.get_or_create_workspace_active(request)
        return self.select_form(request.POST, user=request.user, workspace=self.workspace_active)

    def post_process_select_form(self, request):
        self.component_old = self.bound_select_form.cleaned_data.get(self.component_cls().key)

    def bind_update_form(self, request):
        return self.update_form({**{self.component_old.key:self.component_old}, **to_dict(self.component_old)},
                                    instance=self.component_old,
                                    user=request.user,
                                    workspace=self.workspace_active)

    def post_process_update_form(self, request):
        self.component = self.bound_update_form.save(commit=False)
        self.component.updated = True
        self.component.save()

    def valid_return(self, *args, **kwargs):
        return redirect('home-home')

    def invalid_select_return(self, request, *args, **kwargs):
        context = self.crud_form_context(request)
        context['form'] = self.bound_select_form
        return render(request, self.crud_form_template, context)

    def invalid_update_return(self, request, *args, **kwargs):
        context = self.crud_form_context(request)
        context['form'] = self.bound_update_form
        return render(request, self.crud_form_template, context)

    def post(self, request):
        self.crud_form_template = 'home/home.html'
        self.bound_select_form = self.bind_select_form(request)

        if self.bound_select_form.is_valid():
            self.post_process_select_form(request)
            self.bound_update_form = self.bind_update_form(request)

            if self.bound_update_form.is_valid():
                self.post_process_update_form(request)
                return self.valid_return()

            return self.invalid_select_return(request)
        return self.invalid_update_return(request)

###### DatasetUpload ######
class DeleteDatasetUpload(CRUDComponent):

    def post_process_form(self, request):
        datasetupload = self.bound_form.cleaned_data.get(DatasetUpload().key)
        datasetupload.delete()

    def post(self, request):
        self.form = DeleteDatasetUploadForm
        return super().post(request)

class CreateDatasetUpload(CRUDComponent):

    def post_process_form(self, request):
        # Create/save dataset/datasetupload
        datasetupload = self.bound_form.save(commit=False)

        datasetupload.user = request.user
        datasetupload.dataset.user = request.user

        datasetupload.dataset.save()
        datasetupload.save()

        # Add dataset/datasetupload to workspace_active
        self.workspace_active.datasets.add(datasetupload.dataset)
        self.workspace_active.datasetuploads.add(datasetupload)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'create'
        self.component_cls = DatasetUpload
        self.form = CreateDatasetUploadForm
        return super().post(request)

class UpdateDatasetUpload(CRUDComponent):

    def post_process_form(self, request):
        datasetupload_old = self.bound_form.cleaned_data.get(DatasetUpload().key)
        dataset_old = datasetupload_old.dataset

        datasetupload = self.bound_form.save(commit=False)
        datasetupload.dataset.save()
        datasetupload.save()

    def post(self, request):
        self.crud_type = 'update'
        self.component_cls = DatasetUpload
        self.form = UpdateDatasetUploadForm
        self.select_form = SelectDatasetUploadForm
        return super().post(request)

class DuplicateDatasetUpload(CRUDComponent):

    def post_process_form(self, request):
        # Create/save or update/save dataset/datasetupload
        datasetupload = self.bound_form.save(commit=False)
        datasetupload.user = request.user
        datasetupload.dataset.user = request.user
        datasetupload.dataset.save()
        datasetupload.save()

        # Add dataset/datasetupload to workspace_active
        self.workspace_active.datasets.add(datasetupload.dataset)
        self.workspace_active.datasetuploads.add(datasetupload)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'duplicate'
        self.component_cls = DatasetUpload
        self.form = DuplicateDatasetUploadForm
        return super().post(request)

###### PredictionRegressionXY ######
class DeletePredictionRegressionXY(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.cleaned_data.get(self.component_cls().key)
        component.delete()

    def post(self, request):
        self.crud_type = 'delete'
        return super().post(request)

class CreatePredictionRegressionXY(CRUDComponent):

    def post_process_form(self, request):
        # Create/save y as new dataset, form as new predictionordinaryleastsquares
        component = self.bound_form.save(commit=False)
        component.user = request.user
        y = component.y
        y.save()
        component.save()
        
        # Add y/predictionordinaryleastsquares to workspace_active
        self.workspace_active.datasets.add(y)
        getattr(self.workspace_active, component.key+'s').add(component)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'create'
        return super().post(request)

class UpdatePredictionRegressionXY(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.save(commit=False)
        y = component.y
        
        y.save()
        component.save()

    def post(self, request):
        self.crud_type = 'update'
        return super().post(request)

class DuplicatePredictionRegressionXY(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.save(commit=False)
        y = component.y
        
        y.save()
        component.save()

        # Add y/predictionordinaryleastsquares to workspace_active
        self.workspace_active.datasets.add(y)
        getattr(self.workspace_active, component.key+'s').add(component)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'duplicate'
        return super().post(request)

class RefreshPredictionRegressionXY(RefreshComponent):

    def post_process_select_form(self, request):
        self.component_old = self.bound_select_form.cleaned_data.get(self.component_cls().key)
        self.component_old.y_file = None # Needs to be removed for validation to pass. Recreated in update_form

    def post_process_update_form(self, request):
        self.component = self.bound_update_form.save(commit=False)
        self.component.id = self.component_old.id
        self.component.updated = True
        self.component.y.updated = True
        self.component.y.save()
        self.component.save()

    def post(self, request):
        self.crud_type = 'refresh'
        return super().post(request)

### PredictionOrdinaryLeastSquares ###
class DeletePredictionOrdinaryLeastSquares(DeletePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionOrdinaryLeastSquares
        self.form = DeletePredictionOrdinaryLeastSquaresForm
        return super().post(request)

class CreatePredictionOrdinaryLeastSquares(CreatePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionOrdinaryLeastSquares
        self.form = CreatePredictionOrdinaryLeastSquaresForm
        return super().post(request)

class UpdatePredictionOrdinaryLeastSquares(UpdatePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionOrdinaryLeastSquares
        self.form = UpdatePredictionOrdinaryLeastSquaresForm
        self.select_form = SelectPredictionOrdinaryLeastSquaresForm
        return super().post(request)

class DuplicatePredictionOrdinaryLeastSquares(DuplicatePredictionRegressionXY):

    def post(self, request):
        self.form = DuplicatePredictionOrdinaryLeastSquaresForm
        return super().post(request)

class RefreshPredictionOrdinaryLeastSquares(RefreshPredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionOrdinaryLeastSquares
        self.select_form = SelectPredictionOrdinaryLeastSquaresForm
        self.update_form = UpdatePredictionOrdinaryLeastSquaresForm
        return super().post(request)

### PredictionRidgeRegression ###
class DeletePredictionRidgeRegression(DeletePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionRidgeRegression
        self.form = DeletePredictionRidgeRegressionForm
        return super().post(request)

class CreatePredictionRidgeRegression(CreatePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionRidgeRegression
        self.form = CreatePredictionRidgeRegressionForm
        return super().post(request)

class UpdatePredictionRidgeRegression(UpdatePredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionRidgeRegression
        self.form = UpdatePredictionRidgeRegressionForm
        self.select_form = SelectPredictionRidgeRegressionForm
        return super().post(request)

class DuplicatePredictionRidgeRegression(DuplicatePredictionRegressionXY):

    def post(self, request):
        self.form = DuplicatePredictionRidgeRegressionForm
        return super().post(request)

class RefreshPredictionRidgeRegression(RefreshPredictionRegressionXY):

    def post(self, request):
        self.component_cls = PredictionRidgeRegression
        self.select_form = SelectPredictionRidgeRegressionForm
        self.update_form = UpdatePredictionRidgeRegressionForm
        return super().post(request)

###### Regression ######
class DeleteRegression(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.cleaned_data.get(self.component_cls().key)
        component.delete()

    def post(self, request):
        self.crud_type = 'delete'
        return super().post(request)

class CreateRegression(CRUDComponent):

    def post_process_form(self, request):
        # Create/save ordinaryleastsquares
        component = self.bound_form.save(commit=False)
        component.user = request.user
        component.updated = True
        component.save()

        # Add component to workspace_active
        getattr(self.workspace_active, component.key+'s').add(component)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'create'
        return super().post(request)

class UpdateRegression(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.save(commit=False)
        component.save()

    def invalid_return(self, request, *args, **kwargs):
        context = {'form':self.bound_form, self.component_cls().key:self.component_cls}
        select_form = SelectOrdinaryLeastSquaresForm(request.POST, user=request.user, workspace=self.workspace_active)
        if select_form.is_valid():
            component = select_form.cleaned_data.get(self.component_cls().key)
            context[self.component_cls().key] = component

        return render(request, self.crud_form_template, context)

    def post(self, request):
        self.crud_type = 'update'
        return super().post(request)

class DuplicateRegression(CreateRegression):
    
    def post(self, request):
        self.crud_type = 'duplicate'
        return super().post(request)

class RefreshRegression(RefreshComponent):

    def post_process_select_form(self, request):
        self.component_old = self.bound_select_form.cleaned_data.get(self.component_cls().key)
        self.component_old.reg_file = None # Needs to be removed for validation to pass. Recreated in create_form

    def post(self, request):
        self.crud_type = 'refresh'
        return super().post(request)

### OrdinaryLeastSquares ###
class DeleteOrdinaryLeastSquares(DeleteRegression):

    def post(self, request):
        self.component_cls = OrdinaryLeastSquares
        self.form = DeleteOrdinaryLeastSquaresForm
        return super().post(request) 

class CreateOrdinaryLeastSquares(CreateRegression):

    def post(self, request):
        self.component_cls = OrdinaryLeastSquares
        self.form = CreateOrdinaryLeastSquaresForm
        return super().post(request) 

class UpdateOrdinaryLeastSquares(UpdateRegression):

    def post(self, request):
        self.component_cls = OrdinaryLeastSquares
        self.form = UpdateOrdinaryLeastSquaresForm
        self.select_form = SelectOrdinaryLeastSquaresForm
        return super().post(request)

class DuplicateOrdinaryLeastSquares(DuplicateRegression):
        
    def post(self, request):
        self.component_cls = OrdinaryLeastSquares
        self.form = DuplicateOrdinaryLeastSquaresForm
        return super().post(request)

class RefreshOrdinaryLeastSquares(RefreshRegression):

    def post(self, request):
        self.component_cls = OrdinaryLeastSquares
        self.select_form = SelectOrdinaryLeastSquaresForm
        self.update_form = UpdateOrdinaryLeastSquaresForm
        return super().post(request)

### RidgeRegression ###
class DeleteRidgeRegression(DeleteRegression):

    def post(self, request):
        self.component_cls = RidgeRegression
        self.form = DeleteRidgeRegressionForm
        return super().post(request) 

class CreateRidgeRegression(CreateRegression):

    def post(self, request):
        self.component_cls = RidgeRegression
        self.form = CreateRidgeRegressionForm
        return super().post(request) 

class UpdateRidgeRegression(UpdateRegression):

    def post(self, request):
        self.component_cls = RidgeRegression
        self.form = UpdateRidgeRegressionForm
        self.select_form = SelectRidgeRegressionForm
        return super().post(request)

class DuplicateRidgeRegression(DuplicateRegression):
        
    def post(self, request):
        self.component_cls = RidgeRegression
        self.form = DuplicateRidgeRegressionForm
        return super().post(request)

class RefreshRidgeRegression(RefreshRegression):

    def post(self, request):
        self.component_cls = RidgeRegression
        self.select_form = SelectRidgeRegressionForm
        self.update_form = UpdateRidgeRegressionForm
        return super().post(request)

##### Visualizations #####
class DeleteVisualizationX(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.cleaned_data.get(self.component_cls().key)
        component.delete()

    def post(self, request):
        self.crud_type = 'delete'
        return super().post(request)

class CreateVisualizationX(CRUDComponent):

    def post_process_form(self, request):
        # Create/save scattermatrix
        component = self.bound_form.save(commit=False)
        component.user = request.user
        component.updated = True
        component.save()

        # Add component to workspace_active
        getattr(self.workspace_active, component.key+'s').add(component)
        self.workspace_active.save()

    def post(self, request):
        self.crud_type = 'create'
        return super().post(request)

class UpdateVisualizationX(CRUDComponent):

    def post_process_form(self, request):
        component = self.bound_form.save(commit=False)
        component.save()

    def post(self, request):
        self.crud_type = 'update'
        return super().post(request)

class DuplicateVisualizationX(CreateVisualizationX):

    def post(self, request):
        self.crud_type = 'duplicate'
        return super().post(request)

class RefreshVisualizationX(RefreshComponent):

    def post_process_select_form(self, request):
        self.component_old = self.bound_select_form.cleaned_data.get(self.component_cls().key)
        self.component_old.fig_file = None # Needs to be removed for validation to pass. Recreated in create_form

    def post(self, request):
        self.crud_type = 'refresh'
        return super().post(request)

### Scatter Matrix ###
class DeleteScatterMatrix(DeleteVisualizationX):

    def post(self, request):
        self.component_cls = ScatterMatrix
        self.form = DeleteScatterMatrixForm
        return super().post(request) 

class CreateScatterMatrix(CreateVisualizationX):

    def post(self, request):
        self.component_cls = ScatterMatrix
        self.form = CreateScatterMatrixForm
        return super().post(request) 

class UpdateScatterMatrix(UpdateVisualizationX):

    def post(self, request):
        self.component_cls = ScatterMatrix
        self.form = UpdateScatterMatrixForm
        self.select_form = SelectScatterMatrixForm
        return super().post(request)

class DuplicateScatterMatrix(DuplicateVisualizationX):
        
    def post(self, request):
        self.component_cls = ScatterMatrix
        self.form = DuplicateScatterMatrixForm
        return super().post(request)

class RefreshScatterMatrix(RefreshVisualizationX):

    def post(self, request):
        self.component_cls = ScatterMatrix
        self.select_form = SelectScatterMatrixForm
        self.update_form = UpdateScatterMatrixForm
        return super().post(request)

###### Histogram ######
class DeleteHistogram(DeleteVisualizationX):

    def post(self, request):
        self.component_cls = Histogram
        self.form = DeleteHistogramForm
        return super().post(request) 

class CreateHistogram(CreateVisualizationX):

    def post(self, request):
        self.component_cls = Histogram
        self.form = CreateHistogramForm
        return super().post(request) 

class UpdateHistogram(UpdateVisualizationX):

    def post(self, request):
        self.component_cls = Histogram
        self.form = UpdateHistogramForm
        self.select_form = SelectHistogramForm
        return super().post(request)

class DuplicateHistogram(DuplicateVisualizationX):
        
    def post(self, request):
        self.component_cls = Histogram
        self.form = DuplicateHistogramForm
        return super().post(request)

class RefreshHistogram(RefreshVisualizationX):

    def post(self, request):
        self.component_cls = Histogram
        self.select_form = SelectHistogramForm
        self.update_form = UpdateHistogramForm
        return super().post(request)
