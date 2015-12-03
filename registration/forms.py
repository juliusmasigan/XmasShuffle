from django import forms
from .models import Organization

class OrganizationRegistrationForm(forms.Form):
    organization_name = forms.CharField(label='', max_length=500, widget=forms.TextInput(attrs={
        'placeholder':'Organization',
        'class':'organization-reg-input form-control',
        'autofocus':'',
    }))
