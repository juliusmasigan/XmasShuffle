# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationEmails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_domain', models.CharField(max_length=255, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='emails',
            field=models.ManyToManyField(to='registration.OrganizationEmails'),
        ),
    ]
