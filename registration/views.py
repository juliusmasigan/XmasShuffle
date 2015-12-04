import re

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .forms import OrganizationRegistrationForm, OrganizationMembersForm
from .models import Organization, Member

# Create your views here.
def index(request):
    form = OrganizationRegistrationForm(request.POST or None)

    if form.is_valid():
        org_name = form.cleaned_data['organization_name']

        org = Organization.objects.create(name=org_name)
        org_link = re.sub(r'-', '', str(org.org_link))
        return redirect('members', org_link=org_link)

    context = {'org_form':form}
    return render(request, 'index.html', context)

def members(request, org_link=None):
    form = OrganizationMembersForm(request.POST or None)
    
    if form.is_valid():
        members_email = form.cleaned_data['organization_members']

        emails = []
        for email in members_email.split(', '):
            emails.append(Member(email=email))

    form_action = reverse('members', kwargs={'org_link':org_link})
    context = {'form_action':form_action, 'org_form':form}
    return render(request, 'members.html', context)
