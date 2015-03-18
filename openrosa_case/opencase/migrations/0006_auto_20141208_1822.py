# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0005_auto_20141206_0255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='form',
            old_name='odk_url',
            new_name='form_url',
        ),
        migrations.AddField(
            model_name='form',
            name='submission_url',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='application',
            name='slug',
            field=models.SlugField(unique=True, max_length=100),
            preserve_default=True,
        ),
    ]
