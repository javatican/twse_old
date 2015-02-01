# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20150127_1222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twse_summary_price_downloaded',
            name='is_processed',
        ),
        migrations.AddField(
            model_name='twse_summary_price_downloaded',
            name='index_processed',
            field=models.BooleanField(default=False, verbose_name='index_processed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_summary_price_downloaded',
            name='price_processed',
            field=models.BooleanField(default=False, verbose_name='price_processed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_summary_price_downloaded',
            name='summary_processed',
            field=models.BooleanField(default=False, verbose_name='summary_processed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_summary_price_downloaded',
            name='tri_index_processed',
            field=models.BooleanField(default=False, verbose_name='tri_index_processed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_summary_price_downloaded',
            name='updown_processed',
            field=models.BooleanField(default=False, verbose_name='updown_processed'),
            preserve_default=True,
        ),
    ]
