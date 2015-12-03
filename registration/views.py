from django.shortcuts import render
from .forms import OrganizationRegistrationForm
from .models import Organization

# Create your views here.
def index(request):
    form=OrganizationRegistrationForm(request.POST or None)

    if form.is_valid():
        org_name = form.cleaned_data['organization_name']

    context={'test':'Hello', 'org_form':form}
    return render(request, 'index.html', context)
