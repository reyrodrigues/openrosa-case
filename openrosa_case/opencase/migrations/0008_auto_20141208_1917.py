# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0007_remove_form_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moduledisplayitem',
            name='type',
            field=models.CharField(max_length=20, choices=[(b'case_short', b'List'), (b'case_long', b'Details')]),
            preserve_default=True,
        ),
    ]
