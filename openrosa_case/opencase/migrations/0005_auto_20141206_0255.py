# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0004_auto_20141206_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='slug',
            field=models.SlugField(default='slug', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application',
            name='version',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
