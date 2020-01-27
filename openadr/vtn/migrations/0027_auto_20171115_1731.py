# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-15 17:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vtn', '0026_auto_20171114_2029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='ven_id',
        ),
        migrations.AlterField(
            model_name='drevent',
            name='last_status_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2017, 11, 15, 17, 31, 50, 787561), null=True, verbose_name='Last Status Time'),
        ),
        migrations.AlterField(
            model_name='siteevent',
            name='last_opt_in',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2017, 11, 15, 17, 31, 50, 788617), null=True, verbose_name='Last opt-in'),
        ),
        migrations.AlterField(
            model_name='siteevent',
            name='last_status_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 15, 17, 31, 50, 788532), verbose_name='Last Status Time'),
        ),
    ]
