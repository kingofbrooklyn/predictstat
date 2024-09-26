from django.contrib import admin
from .models import Workspace,\
                    Dataset,\
                    DatasetUpload,\
                    OrdinaryLeastSquares, RidgeRegression,\
                    PredictionOrdinaryLeastSquares, PredictionRidgeRegression,\
                    ScatterMatrix, Histogram

admin.site.register(Workspace)

admin.site.register(Dataset)
admin.site.register(DatasetUpload)

admin.site.register(OrdinaryLeastSquares)
admin.site.register(RidgeRegression)

admin.site.register(PredictionOrdinaryLeastSquares)
admin.site.register(PredictionRidgeRegression)

admin.site.register(ScatterMatrix)
admin.site.register(Histogram)
