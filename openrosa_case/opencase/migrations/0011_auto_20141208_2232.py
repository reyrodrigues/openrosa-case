# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0010_applicationuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=100)),
                ('application', models.ForeignKey(to='opencase.Application')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicationuser',
            name='uuid',
            field=models.CharField(default='000000000000000000000000000000', max_length=64),
            preserve_default=False,
        ),
    ]
