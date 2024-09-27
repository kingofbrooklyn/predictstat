from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser

class RegisterForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class LoginForm(AuthenticationForm):
    """Login to account form"""
    pass

class UpdateAccountForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']
    

