# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150125_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading',
            name='closing_price',
            field=models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='highest_price',
            field=models.DecimalField(default=0, verbose_name='highest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='lowest_price',
            field=models.DecimalField(default=0, verbose_name='lowest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='opening_price',
            field=models.DecimalField(default=0, verbose_name='opening_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='price_change',
            field=models.DecimalField(default=0, verbose_name='price_change', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='trade_transaction',
            field=models.PositiveIntegerField(default=0, verbose_name='trade_transaction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='trade_value',
            field=models.PositiveIntegerField(default=0, verbose_name='trade_value'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='trade_volume',
            field=models.PositiveIntegerField(default=0, verbose_name='trade_volume'),
            preserve_default=True,
        ),
    ]
