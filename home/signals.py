from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from .models import DatasetUpload,\
                    PredictionOrdinaryLeastSquares, PredictionRidgeRegression,\
                    OrdinaryLeastSquares, RidgeRegression,\
                    ScatterMatrix, Histogram

"""
Whenever a record is deleted, check if it has any file fields associated, and delete the files from storage.
"""
@receiver(post_delete)
def post_delete_delete_file_fields(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if field.get_internal_type() == 'FileField':
            if getattr(instance, field.name):
                getattr(instance, field.name).delete(False) # Pass false so FileField doesn't save the model.
