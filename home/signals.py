from django.db.models.signals import post_delete, post_save
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

"""
When DatasetUpload is saved, ensure the related Dataset.df_file filepath is updated.
"""
@receiver(post_save, sender=DatasetUpload)
def post_save_updates(sender, instance, **kwargs):
        # Ensure dependent components are shown as potentially old versions
        instance.dataset.updated = False
        # Ensure path to file is updated on dataset
        instance.dataset.df_file = instance.df_file.path
        instance.dataset.save()