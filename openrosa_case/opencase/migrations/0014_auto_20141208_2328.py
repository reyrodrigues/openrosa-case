# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0013_auto_20141208_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationuser',
            name='created_on',
            field=models.DateField(default=datetime.datetime(2014, 12, 8, 23, 28, 35, 198183, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='applicationkey',
            name='key',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]
