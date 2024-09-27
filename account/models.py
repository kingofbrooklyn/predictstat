from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    name_singular = "User"
    name_plural = "Users"

    def __str__(self):
        return str(self.username)

    @property
    def key(self):
        return 'user'

    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email" # make the user log in with the email
    REQUIRED_FIELDS = ['username']
