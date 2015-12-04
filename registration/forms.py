from django import forms
from .models import Organization

class OrganizationRegistrationForm(forms.Form):
    organization_name = forms.CharField(label='', max_length=500, widget=forms.TextInput(attrs={
        'placeholder':'Organization',
        'class':'organization-reg-input form-control',
        'autofocus':'',
    }))

class OrganizationMembersForm(forms.Form):
    organization_members = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder':'Member Emails',
        'class':'organization-reg-input form-control',
        'autofocus':'',
    }))
