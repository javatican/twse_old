# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150121_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock_item',
            name='data_available',
        ),
        migrations.RemoveField(
            model_name='stock_item',
            name='missing_info',
        ),
        migrations.RemoveField(
            model_name='warrant_item',
            name='data_available',
        ),
        migrations.RemoveField(
            model_name='warrant_item',
            name='missing_info',
        ),
        migrations.AddField(
            model_name='stock_item',
            name='data_downloaded',
            field=models.BooleanField(default=False, verbose_name='data_downloaded'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='data_ok',
            field=models.BooleanField(default=False, verbose_name='data_ok'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='parsing_error',
            field=models.BooleanField(default=False, verbose_name='parsing_error'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='data_downloaded',
            field=models.BooleanField(default=False, verbose_name='data_downloaded'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='data_ok',
            field=models.BooleanField(default=False, verbose_name='data_ok'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='parsing_error',
            field=models.BooleanField(default=False, verbose_name='parsing_error'),
            preserve_default=True,
        ),
    ]
