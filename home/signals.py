from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from .models import DatasetUpload,\
                    PredictionOrdinaryLeastSquares, PredictionRidgeRegression,\
                    OrdinaryLeastSquares, RidgeRegression,\
                    ScatterMatrix, Histogram

###### Delete associated file when model db row is deleted #####
### DatasetUpload ###
@receiver(post_delete, sender=DatasetUpload)
def delete_file_fields_post_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.df_file:
        instance.df_file.delete(False)

### PredictionOrdinaryLeastSquares ###
@receiver(post_delete, sender=PredictionOrdinaryLeastSquares)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.y_file:
        instance.y_file.delete(False)
### PredictionRidgeRegression ###
@receiver(post_delete, sender=PredictionRidgeRegression)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.y_file:
        instance.y_file.delete(False)

### OrdinaryLeastSquares ###
@receiver(post_delete, sender=OrdinaryLeastSquares)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.reg_file:
        instance.reg_file.delete(False)
### RidgeRegression ###
@receiver(post_delete, sender=RidgeRegression)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.reg_file:
        instance.reg_file.delete(False)

### ScatterMatrix ###
@receiver(post_delete, sender=ScatterMatrix)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.fig_file:
        instance.fig_file.delete(False)
### Histogram ###
@receiver(post_delete, sender=Histogram)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.fig_file:
        instance.fig_file.delete(False)
