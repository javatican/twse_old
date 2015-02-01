# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_twse_price_downloaded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twse_trading',
            name='fi_buy',
            field=models.DecimalField(default=0, verbose_name='fi_buy', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='fi_diff',
            field=models.DecimalField(default=0, verbose_name='fi_diff', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='fi_sell',
            field=models.DecimalField(default=0, verbose_name='fi_sell', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='hedge_buy',
            field=models.DecimalField(default=0, verbose_name='hedge_buy', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='hedge_diff',
            field=models.DecimalField(default=0, verbose_name='hedge_diff', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='hedge_sell',
            field=models.DecimalField(default=0, verbose_name='hedge_sell', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='proprietary_buy',
            field=models.DecimalField(default=0, verbose_name='proprietary_buy', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='proprietary_diff',
            field=models.DecimalField(default=0, verbose_name='proprietary_diff', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='proprietary_sell',
            field=models.DecimalField(default=0, verbose_name='proprietary_sell', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='sit_buy',
            field=models.DecimalField(default=0, verbose_name='sit_buy', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='sit_diff',
            field=models.DecimalField(default=0, verbose_name='sit_diff', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='sit_sell',
            field=models.DecimalField(default=0, verbose_name='sit_sell', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='total_diff',
            field=models.DecimalField(default=0, verbose_name='total_diff', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='trade_transaction',
            field=models.DecimalField(default=0, verbose_name='trade_transaction', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='trade_value',
            field=models.DecimalField(default=0, verbose_name='trade_value', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading',
            name='trade_volume',
            field=models.DecimalField(default=0, verbose_name='trade_volume', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
    ]
