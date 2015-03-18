# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.PositiveIntegerField(default=0, null=True)),
                ('uuid', models.CharField(max_length=100, null=True, blank=True)),
                ('namespace', models.CharField(max_length=100, null=True, blank=True)),
                ('odk_url', models.CharField(max_length=200, null=True, blank=True)),
                ('icon_xpath', models.CharField(max_length=200, null=True, blank=True)),
                ('audio_xpath', models.CharField(max_length=200, null=True, blank=True)),
                ('display_condition', models.CharField(max_length=300, null=True, blank=True)),
                ('end_of_form', models.CharField(blank=True, max_length=20, null=True, choices=[(b'default', b'Home Screen'), (b'module', b'Module'), (b'previous_screen', b'Previous Screen')])),
                ('auto_capture_location', models.BooleanField(default=False)),
                ('case_type', models.CharField(blank=True, max_length=20, null=True, choices=[(b'none', b'Does not use cases'), (b'open', b'Registers a new case'), (b'update', b'Updates or closes a case'), (b'open-other', b'Registers a case (different module)')])),
                ('close_case', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('case_filter', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormCaseMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('direction', models.IntegerField(default=1, null=True, blank=True, choices=[(1, b'From Case'), (2, b'To Case')])),
                ('origin', models.CharField(max_length=500, null=True, blank=True)),
                ('destination', models.CharField(max_length=100, null=True, blank=True)),
                ('form_case', models.ForeignKey(to='opencase.FormCase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.PositiveIntegerField(default=0, null=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('in_root', models.BooleanField(default=False)),
                ('icon_xpath', models.CharField(max_length=200, null=True, blank=True)),
                ('audio_xpath', models.CharField(max_length=200, null=True, blank=True)),
                ('case_type', models.CharField(max_length=100, null=True, blank=True)),
                ('case_label', models.CharField(max_length=100, null=True, blank=True)),
                ('case_menu_item', models.BooleanField(default=False)),
                ('case_menu_item_label', models.CharField(max_length=100, null=True, blank=True)),
                ('case_select_parent', models.BooleanField(default=False)),
                ('case_parent_case', models.ForeignKey(related_name='child_cases', blank=True, to='opencase.Module', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDisplayItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(choices=[(1, b'List'), (2, b'Details')])),
                ('property', models.CharField(max_length=200, null=True, blank=True)),
                ('label', models.CharField(max_length=200, null=True, blank=True)),
                ('format', models.CharField(blank=True, max_length=20, null=True, choices=[(b'plain', b'Plain'), (b'date', b'Date'), (b'time-ago', b'Time Since or Until Date'), (b'phone', b'Phone Number'), (b'enum', b'ID Mapping'), (b'late-flag', b'Late Flag'), (b'invisible', b'Search Only'), (b'address', b'Address (Android/CloudCare)')])),
                ('module', models.ForeignKey(related_name='case_list_items', to='opencase.Module')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='formcase',
            name='case_module',
            field=models.ForeignKey(blank=True, to='opencase.Module', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='formcase',
            name='form',
            field=models.ForeignKey(to='opencase.Form'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='form',
            name='module',
            field=models.ForeignKey(related_name='forms', to='opencase.Module', null=True),
            preserve_default=True,
        ),
    ]
