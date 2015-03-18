# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opencase', '0012_auto_20141208_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=64, blank=True)),
                ('valid', models.DateTimeField(auto_now=True)),
                ('expires', models.DateTimeField()),
                ('key', models.TextField()),
                ('application', models.ForeignKey(related_name='keys', to='opencase.Application')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='applicationgroup',
            name='uuid',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='uuid',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
