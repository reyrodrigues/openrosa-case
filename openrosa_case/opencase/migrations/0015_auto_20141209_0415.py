# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0014_auto_20141208_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationkey',
            name='valid',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='created_on',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
