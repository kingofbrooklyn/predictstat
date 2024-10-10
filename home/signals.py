from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from .models import DatasetUpload,\
                    PredictionOrdinaryLeastSquares, PredictionRidgeRegression,\
                    OrdinaryLeastSquares, RidgeRegression,\
                    ScatterMatrix, Histogram

"""
Whenever a record is deleted, check if it has any file fields associated, 
and delete the files from storage.
"""
@receiver(post_delete)
def post_delete_delete_file_fields(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if field.get_internal_type() == 'FileField':
            if getattr(instance, field.name):
                getattr(instance, field.name).delete(False) # Pass false so FileField doesn't save the model.

"""
When a DatasetUpload is saved, modify the related Dataset so that
-updated is False
-the df_file field is set to the path string
"""
@receiver(post_save, sender=DatasetUpload)
def post_save_updates(sender, instance, **kwargs):
    # Ensure dependent components are shown as potentially old versions
    instance.dataset.updated = False
    # Ensure path to file is updated on dataset
    instance.dataset.df_file = instance.df_file.path
    instance.dataset.save()

"""
Ensure path to file is updated on Dataset for predicted data
"""
@receiver(post_save, sender=[PredictionOrdinaryLeastSquares,PredictionRidgeRegression])
def post_save_updates(sender, instance, **kwargs):
    instance.y.df_file = instance.y_file.path
    instance.y.save()