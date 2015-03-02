# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core2', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gt_stock_item',
            name='data_downloaded',
        ),
        migrations.RemoveField(
            model_name='gt_stock_item',
            name='parsing_error',
        ),
        migrations.RemoveField(
            model_name='gt_summary_price_downloaded',
            name='data_available',
        ),
        migrations.RemoveField(
            model_name='gt_summary_price_downloaded',
            name='highlight_processed',
        ),
        migrations.RemoveField(
            model_name='gt_summary_price_downloaded',
            name='price_processed',
        ),
        migrations.RemoveField(
            model_name='gt_summary_price_downloaded',
            name='summary_processed',
        ),
        migrations.RemoveField(
            model_name='gt_trading_downloaded',
            name='data_available',
        ),
        migrations.RemoveField(
            model_name='gt_trading_downloaded',
            name='is_processed',
        ),
        migrations.RemoveField(
            model_name='gt_warrant_item',
            name='data_downloaded',
        ),
        migrations.RemoveField(
            model_name='gt_warrant_item',
            name='parsing_error',
        ),
        migrations.AlterField(
            model_name='gt_stock_item',
            name='type_code',
            field=models.CharField(default=b'2', max_length=1, verbose_name='stock_type', choices=[(b'1', '\u4e0a\u5e02'), (b'2', '\u4e0a\u6ac3')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gt_warrant_item',
            name='classification',
            field=models.CharField(default=1, max_length=1, verbose_name='classification', choices=[(b'1', '\u8a8d\u8cfc'), (b'2', '\u8a8d\u552e')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gt_warrant_item',
            name='exercise_style',
            field=models.CharField(default=1, max_length=1, verbose_name='exercise_style', choices=[(b'1', '\u6b50\u5f0f'), (b'2', '\u7f8e\u5f0f')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gt_warrant_item',
            name='type_code',
            field=models.CharField(default=b'2', max_length=1, verbose_name='stock_type', choices=[(b'1', '\u4e0a\u5e02'), (b'2', '\u4e0a\u6ac3')]),
            preserve_default=True,
        ),
    ]
