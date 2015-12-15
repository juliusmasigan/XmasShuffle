import re
import django_rq
import random

from urlparse import urlunsplit

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.core.mail import send_mail

from .forms import OrganizationRegistrationForm, OrganizationMembersForm, WishForm
from .models import Organization, Member


SENDER = 'automailer@domain.com'
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
        'You are invited to {0} Kris Kringle!\n\n' \
        'Open the link below to make a wish:\n{1}'.format(member.organization.name, member_link)

    	django_rq.enqueue(
			send_mail,
			subject='Kris Kringle',
			message=message_body, 
			from_email=SENDER,
			recipient_list=[member.email,],
			fail_silently=False
		)

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

	# Fetch again the registered members.
	reg_members = Member.objects.filter(organization=org)
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

def resend_notification(members):
    for member in members:
        message_body = 'Your wish come true!\n\n' \
        'Kindly make your wish using the link below:\n{0}\n\n' \
        'Deadline: Friday (Dec 11) at 12:00PM\n\n' \
        'Shuffling will be done on Friday as well so make sure your wish has been listed!'.format(member.member_link)

        django_rq.enqueue(
            send_mail,
            subject='Kris Kringle',
            message=message_body, 
            from_email=SENDER,
            recipient_list=[member.email,],
            fail_silently=False
        )

def shuffle_members(members):
	members_id = []
	for member in members:
		if not member.id in members_id:
			members_id.append(member.id)

	pairings = []
	random.shuffle(members_id)
	mail_subject = 'Kris Kringle'
	message_body = 'You picked {0}!\n\n{0} wishes to have at least one of the following:\n{1}'
	for index in range(len(members_id)):
		try:
			pair = members.get(pk=members_id[index])
			riap = members.get(pk=members_id[index+1])
		except IndexError:
			pair = members.get(pk=members_id[index])
			riap = members.get(pk=members_id[0])
		finally:
			django_rq.enqueue(
				send_mail,
				subject=mail_subject,
				message=message_body.format(riap.code_name, riap.wish_list), 
				from_email=SENDER,
				recipient_list=[pair.email,],
				fail_silently=False
			)

def shuffle(request, org_link=None):
    global URL_PARTS
    URL_PARTS = {'scheme':request.META.get('wsgi.url_scheme'), 'netloc':request.META.get('HTTP_HOST')}
    members = Member.objects.filter(organization__org_link=org_link)

    lazy_members_email = []
    lazy_members = []
    for member in members:
        path_link = reverse('wish', kwargs={'member_link':re.sub('-', '', str(member.member_link))})
        member_link = urlunsplit((URL_PARTS['scheme'], URL_PARTS['netloc'], path_link, '', ''))
        member.member_link = member_link
        if len(member.code_name.strip()) == 0 or len(member.wish_list.strip()) == 0:
            lazy_members.append(member)
            lazy_members_email.append(member.email)

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'resend_notif':
            resend_notification(lazy_members)
        else:
            shuffle_members(members)

    context = {'members':members, 'lazy_members_email':lazy_members_email, 'org_link':org_link}
    return render(request, 'shuffle.html', context)
