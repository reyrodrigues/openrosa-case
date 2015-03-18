# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0011_auto_20141208_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationuser',
            name='group',
            field=models.ForeignKey(blank=True, to='opencase.ApplicationGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationgroup',
            name='application',
            field=models.ForeignKey(related_name='groups', to='opencase.Application'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='application',
            field=models.ForeignKey(related_name='users', to='opencase.Application'),
            preserve_default=True,
        ),
    ]
