import uuid

from django.db import models

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=500, db_index=True)
    org_link = models.UUIDField(default=uuid.uuid4, editable=False)

class Member(models.Model):
    organization = models.ForeignKey(Organization)
    email = models.CharField(max_length=255, db_index=True)
    code_name = models.CharField(max_length=255, db_index=True)
    wish_list = models.TextField()
