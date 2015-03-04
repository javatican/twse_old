# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20150303_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='delta',
            field=models.DecimalField(null=True, verbose_name='delta', max_digits=7, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='implied_volatility',
            field=models.DecimalField(null=True, verbose_name='implied_volatility', max_digits=6, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='leverage',
            field=models.DecimalField(null=True, verbose_name='leverage', max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='time_to_maturity',
            field=models.DecimalField(null=True, verbose_name='time_to_maturity', max_digits=6, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='calc_warrant_price',
            field=models.DecimalField(null=True, verbose_name='calc_warrant_price', max_digits=12, decimal_places=4),
            preserve_default=True,
        ),
    ]
