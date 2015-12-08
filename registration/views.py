import re

from urlparse import urlunsplit

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.core.mail import send_mass_mail

from .forms import OrganizationRegistrationForm, OrganizationMembersForm, WishForm
from .models import Organization, Member


SENDER = 'Automailer'
URL_PARTS = {}
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
    messages = None
    for member in members:
        path_link = reverse('wish', kwargs={'member_link':re.sub('-', '', str(member.member_link))})
        member_link = urlunsplit((URL_PARTS['scheme'], URL_PARTS['netloc'], path_link, '', ''))
        message_body = 'Your wish come true!\n' \
        'You are invited to {0} Chris Kringle!\n\n' \
        'Open the link below to make a wish:\n{1}'.format(member.organization.name, member_link)
        if messages is None:
            messages = (('Chris Kringle', message_body, SENDER, [member.email]),)
        else:
            messages = messages + (('Chris Kringle', message_body, SENDER, [member.email]),)

    sent = send_mass_mail(messages, fail_silently=False)
    return sent

def create_members(org, new_emails=[]):
    new_emails_obj = []
    if new_emails:
        for new_email in new_emails:
            new_emails_obj.append(Member(email=new_email, organization=org))

        members = Member.objects.bulk_create(new_emails_obj)
        invite_members(members)

    return members

def remove_members(org, del_emails=[]):
	if del_emails:
		del_members = Member.objects.filter(email__in=del_emails, organization=org)
		del_members.delete()

def members(request, org_link=None):
	global URL_PARTS
	URL_PARTS = {'scheme':request.META.get('wsgi.url_scheme'), 'netloc':request.META.get('HTTP_HOST')}
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
	do_shuffle = True if reg_members.count() > 1 else False
	context = {'form_action':form_action, 'org_form':form, 'org_link':org_link, 'do_shuffle':do_shuffle}
	return render(request, 'members.html', context)

def wish(request, member_link=None):
    form = WishForm(request.POST or None)
    member = get_object_or_404(Member, member_link=member_link)

    form_success = False
    if form.is_valid():
        code_name = form.cleaned_data['code_name']
        wish_list = form.cleaned_data['wish_list']
        member.code_name = code_name
        member.wish_list = wish_list
        member.save()
        form_success = True

    form.initial = {'code_name':member.code_name, 'wish_list':member.wish_list}
    form_action = reverse('wish', kwargs={'member_link':member_link})
    context = {'form_action':form_action, 'wish_form':form, 'form_success':form_success}
    return render(request, 'wish.html', context)

def shuffle(request, org_link=None):
	if request.method == "POST":
		print "SHUFFLE"
	
	return render(request, 'shuffle.html')
