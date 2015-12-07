import re

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.core.mail import send_mail

from .forms import OrganizationRegistrationForm, OrganizationMembersForm
from .models import Organization, Member

# Create your views here.
def index(request):
    form = OrganizationRegistrationForm(request.POST or None)

    if form.is_valid():
        org_name = form.cleaned_data['organization_name']

		# Register the organization and give unique link.
        org = Organization.objects.create(name=org_name)
        org_link = re.sub(r'-', '', str(org.org_link))

		# List all the members after creating the organization.
        return redirect('members', org_link=org_link)

    context = {'org_form':form}
    return render(request, 'index.html', context)

def invite_members(members=None):
	messages = ()
	for member in members:
		message_body = 'You\'re wish come true.\n\n' \
		+ 'You are invited to {} Chris Kringle!\n' \
		+ 'Visit this the link below to make a wish:\n\n{}'.format(member.organization.name, member.member_link)
		messages.append(('Chris Kringle', message_body, member.member_link

def create_members(org, new_emails=[]):
	new_emails_obj = []
	if new_emails:
		for new_email in new_emails:
			new_emails_obj.append(Member(email=new_email, organization=org))

		members = Member.objects.bulk_create(new_emails_obj)
		invite_members(members)

def remove_members(org, del_emails=[]):
	if del_emails:
		del_members = Member.objects.filter(email__in=del_emails)
		del_members.delete()

def members(request, org_link=None):
	form = OrganizationMembersForm(request.POST or None)
	org = get_object_or_404(Organization, org_link=org_link)

	reg_members = Member.objects.filter(organization=org)
	reg_emails = []
	for reg_member in reg_members:
		reg_emails.append(reg_member.email)

	if form.is_valid():
		members_email = form.cleaned_data['organization_members']
		email_list = filter(None, members_email.split(', '))

		# Get the registered members from the email list then segregate it
		# it from the unregistered ones.
		new_emails = set(set(email_list)-set(reg_emails))
		if new_emails:
			create_members(org, new_emails)

		# Get the removed members.
		del_emails = set(set(reg_emails)-set(email_list))
		if del_emails:
			remove_members(org, del_emails)

	# Prepopulate the members field.
	form.initial = {'organization_members':', '.join(reg_emails)}
	form_action = reverse('members', kwargs={'org_link':org_link})
	context = {'form_action':form_action, 'org_form':form}
	return render(request, 'members.html', context)
