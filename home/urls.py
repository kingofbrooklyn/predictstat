"""home URL Configuration"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home-home'),\

    path('create-workspace', views.create_workspace, name='home-create-workspace'),\
    path('home-select-workspace', views.select_workspace, name='home-select-workspace'),\



    path('delete-datasetupload', views.DeleteDatasetUpload.as_view(), name='home-delete-datasetupload'),\
    path('create-datasetupload', views.CreateDatasetUpload.as_view(), name='home-create-datasetupload'),\
    path('update-datasetupload', views.UpdateDatasetUpload.as_view(), name='home-update-datasetupload'),\
    path('duplicate-datasetupload', views.DuplicateDatasetUpload.as_view(), name='home-duplicate-datasetupload'),\
    


    path('delete-predictionordinaryleastsquares', views.DeletePredictionOrdinaryLeastSquares.as_view(), name='home-delete-predictionordinaryleastsquares'),\
    path('create-predictionordinaryleastsquares', views.CreatePredictionOrdinaryLeastSquares.as_view(), name='home-create-predictionordinaryleastsquares'),\
    path('update-predictionordinaryleastsquares', views.UpdatePredictionOrdinaryLeastSquares.as_view(), name='home-update-predictionordinaryleastsquares'),\
    path('duplicate-predictionordinaryleastsquares', views.DuplicatePredictionOrdinaryLeastSquares.as_view(), name='home-duplicate-predictionordinaryleastsquares'),\
    path('refresh-predictionordinaryleastsquares', views.RefreshPredictionOrdinaryLeastSquares.as_view(), name='home-refresh-predictionordinaryleastsquares'),\
    
    path('delete-predictionridgeregression', views.DeletePredictionRidgeRegression.as_view(), name='home-delete-predictionridgeregression'),\
    path('create-predictionridgeregression', views.CreatePredictionRidgeRegression.as_view(), name='home-create-predictionridgeregression'),\
    path('update-predictionridgeregression', views.UpdatePredictionRidgeRegression.as_view(), name='home-update-predictionridgeregression'),\
    path('duplicate-predictionridgeregression', views.DuplicatePredictionRidgeRegression.as_view(), name='home-duplicate-predictionridgeregression'),\
    path('refresh-predictionridgeregression', views.RefreshPredictionRidgeRegression.as_view(), name='home-refresh-predictionridgeregression'),\
    


    path('delete-ordinaryleastsquares', views.DeleteOrdinaryLeastSquares.as_view(), name='home-delete-ordinaryleastsquares'),\
    path('create-ordinaryleastsquares', views.CreateOrdinaryLeastSquares.as_view(), name='home-create-ordinaryleastsquares'),\
    path('update-ordinaryleastsquares', views.UpdateOrdinaryLeastSquares.as_view(), name='home-update-ordinaryleastsquares'),\
    path('duplicate-ordinaryleastsquares', views.DuplicateOrdinaryLeastSquares.as_view(), name='home-duplicate-ordinaryleastsquares'),\
    path('refresh-ordinaryleastsquares', views.RefreshOrdinaryLeastSquares.as_view(), name='home-refresh-ordinaryleastsquares'),\
    
    path('delete-ridgeregression', views.DeleteRidgeRegression.as_view(), name='home-delete-ridgeregression'),\
    path('create-ridgeregression', views.CreateRidgeRegression.as_view(), name='home-create-ridgeregression'),\
    path('update-ridgeregression', views.UpdateRidgeRegression.as_view(), name='home-update-ridgeregression'),\
    path('duplicate-ridgeregression', views.DuplicateRidgeRegression.as_view(), name='home-duplicate-ridgeregression'),\
    path('refresh-ridgeregression', views.RefreshRidgeRegression.as_view(), name='home-refresh-ridgeregression'),\



    path('delete-scattermatrix', views.DeleteScatterMatrix.as_view(), name='home-delete-scattermatrix'),\
    path('create-scattermatrix', views.CreateScatterMatrix.as_view(), name='home-create-scattermatrix'),\
    path('update-scattermatrix', views.UpdateScatterMatrix.as_view(), name='home-update-scattermatrix'),\
    path('duplicate-scattermatrix', views.DuplicateScatterMatrix.as_view(), name='home-duplicate-scattermatrix'),\
    path('refresh-scattermatrix', views.RefreshScatterMatrix.as_view(), name='home-refresh-scattermatrix'),\

    path('delete-histogram', views.DeleteHistogram.as_view(), name='home-delete-histogram'),\
    path('create-histogram', views.CreateHistogram.as_view(), name='home-create-histogram'),\
    path('update-histogram', views.UpdateHistogram.as_view(), name='home-update-histogram'),\
    path('duplicate-histogram', views.DuplicateHistogram.as_view(), name='home-duplicate-histogram'),\
    path('refresh-histogram', views.RefreshHistogram.as_view(), name='home-refresh-histogram'),\
]
