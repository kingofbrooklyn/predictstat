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
    
class SelectUserForm(forms.Form):

    user = forms.ModelChoiceField(queryset=CustomUser.objects.none())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SelectUserForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(id=self.user.id)

class DeleteUserForm(SelectUserForm):
    pass
