from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class UserRegisterForm(UserCreationForm):
    """ Форма регистрации """
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Имя пользователя'}
        ))
    
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-input', 'placeholder': 'Пароль'}
        ))

    password2 = forms.CharField(label='Пароль еще раз', widget=forms.PasswordInput(
        attrs={'class': 'form-input', 'placeholder': 'Пароль еще раз'}
        ))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    """ Форма авторизации"""
    username = forms.CharField(label='Username', widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Имя пользователя'}
        ))

    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-input', 'placeholder': 'Пароль'}
        ))
