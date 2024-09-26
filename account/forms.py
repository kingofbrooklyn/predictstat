from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class LoginForm(AuthenticationForm):
    """Login to account form"""
    pass

