from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Student

class CustomUserCreationForm(UserCreationForm):
    guardian_name = forms.CharField(max_length=40, required=True)
    guardian_relationship = forms.CharField(max_length=50, required=True)
    guardian_email = forms.EmailField(required=True)
    guardian_phone_number = forms.CharField(max_length=15, required=True)
    guardian_whatsapp_number = forms.CharField(max_length=15, required=True)
    guardian_alternate_number = forms.CharField(max_length=15, required=False)
    bank_statement = forms.FileField(required = False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'guardian_name', 'guardian_relationship', 'guardian_email', 'guardian_phone_number', 'guardian_whatsapp_number', 'guardian_alternate_number','bank_statement')