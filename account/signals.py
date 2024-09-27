from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
import shutil
from predictstat.settings import MEDIA_ROOT
from .models import CustomUser

@receiver(post_delete, sender=CustomUser)
def delete_file_fields_post_delete(sender, instance, **kwargs):
    shutil.rmtree(MEDIA_ROOT+'\\user_{0}'.format(instance.id))