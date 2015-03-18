# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0002_auto_20141205_2212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='form',
            old_name='case_type',
            new_name='case_actions',
        ),
        migrations.AlterField(
            model_name='formcase',
            name='form',
            field=models.ForeignKey(related_name='cases', to='opencase.Form'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formcasemapping',
            name='form_case',
            field=models.ForeignKey(related_name='mapping', to='opencase.FormCase'),
            preserve_default=True,
        ),
    ]
