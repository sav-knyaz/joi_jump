#from .models import Task
from django import forms
from django.forms import ModelForm, TextInput, DateInput, PasswordInput
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Registration(forms.Form):
    
    phone = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Номер телефона',
    }))
    password = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Пароль'
    }))
    surname = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Фамилия'
    }))
    first_name = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Имя Отчество'
    }))
    birthday = forms.DateField(widget=DateInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'type':'date'

    }))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 10:
            raise ValidationError('Номер должен быть длиной в 10 символов (без +7 или 8)')
        return phone
 

class LoginForms(forms.Form):

    phone = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Номер телефона'
    }), validators=[RegexValidator(r'\d*9|admin')], max_length=10) 

    password = forms.CharField(widget=PasswordInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Пароль'
    }))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 10:
            raise ValidationError('Номер должен быть длиной в 10 символов (без +7 или 8)')
        return phone


class FormXcode(forms.Form):

    xcode = forms.CharField(widget=TextInput(attrs={
        'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Введите код'
    }), max_length=4)

class FormPhone(forms.Form):

    phone = forms.CharField(widget=TextInput(attrs={
            'class':'form-control',
            'style': 'width: 100%; ',
            'placeholder':'Номер телефона'
    }), validators=[RegexValidator(r'\d*9|admin')], max_length=10)