from django import forms
from .models import Organization

class OrganizationRegistrationForm(forms.Form):
    organization_name = forms.CharField(label='', max_length=500, widget=forms.TextInput(attrs={
        'placeholder':'Organization',
        'class':'organization-reg-input form-control',
        'autofocus':'',
    }))

class OrganizationMembersForm(forms.Form):
    organization_members = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={
        'placeholder':'Members Email Address',
        'class':'organization-reg-input form-control',
        'autofocus':'',
    }))

class WishForm(forms.Form):
	code_name = forms.CharField(label='', max_length=255, widget=forms.TextInput(attrs={
		'placeholder':'Codename: 2015 Hollywood/Local Movie Character',
		'class':'form-control wish-codename-input',
		'autofocus':'',
	}))
	wish_list = forms.CharField(label='', widget=forms.Textarea(attrs={
		'placeholder':'List your wishes here. Put numbers 1-3.',
		'class':'form-control wish-list-input',
		'rows':'5',
	}))
