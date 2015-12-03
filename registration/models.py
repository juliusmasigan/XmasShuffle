from django.db import models

# Create your models here.

class OrganizationEmails(models.Model):
    email_domain = models.CharField(max_length=255, db_index=True)

class Organization(models.Model):
    name = models.CharField(max_length=500, db_index=True)
    emails = models.ManyToManyField(OrganizationEmails)
    #logo = models.ImageField(upload_to='uploads/org_logo/')
