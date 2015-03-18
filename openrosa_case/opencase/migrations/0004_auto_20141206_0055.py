# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0003_auto_20141206_0022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='form',
            old_name='case_actions',
            new_name='case_action',
        ),
    ]
