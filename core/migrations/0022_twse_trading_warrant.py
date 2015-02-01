# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20150127_1228'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twse_Trading_Warrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_diff', models.DecimalField(default=0, verbose_name='total_diff', max_digits=15, decimal_places=0)),
                ('fi_buy', models.DecimalField(default=0, verbose_name='fi_buy', max_digits=15, decimal_places=0)),
                ('fi_sell', models.DecimalField(default=0, verbose_name='fi_sell', max_digits=15, decimal_places=0)),
                ('fi_diff', models.DecimalField(default=0, verbose_name='fi_diff', max_digits=15, decimal_places=0)),
                ('sit_buy', models.DecimalField(default=0, verbose_name='sit_buy', max_digits=15, decimal_places=0)),
                ('sit_sell', models.DecimalField(default=0, verbose_name='sit_sell', max_digits=15, decimal_places=0)),
                ('sit_diff', models.DecimalField(default=0, verbose_name='sit_diff', max_digits=15, decimal_places=0)),
                ('proprietary_buy', models.DecimalField(default=0, verbose_name='proprietary_buy', max_digits=15, decimal_places=0)),
                ('proprietary_sell', models.DecimalField(default=0, verbose_name='proprietary_sell', max_digits=15, decimal_places=0)),
                ('proprietary_diff', models.DecimalField(default=0, verbose_name='proprietary_diff', max_digits=15, decimal_places=0)),
                ('hedge_buy', models.DecimalField(default=0, verbose_name='hedge_buy', max_digits=15, decimal_places=0)),
                ('hedge_sell', models.DecimalField(default=0, verbose_name='hedge_sell', max_digits=15, decimal_places=0)),
                ('hedge_diff', models.DecimalField(default=0, verbose_name='hedge_diff', max_digits=15, decimal_places=0)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('trade_volume', models.DecimalField(default=0, verbose_name='trade_volume', max_digits=15, decimal_places=0)),
                ('trade_transaction', models.DecimalField(default=0, verbose_name='trade_transaction', max_digits=15, decimal_places=0)),
                ('trade_value', models.DecimalField(default=0, verbose_name='trade_value', max_digits=15, decimal_places=0)),
                ('opening_price', models.DecimalField(default=0, verbose_name='opening_price', max_digits=10, decimal_places=2)),
                ('highest_price', models.DecimalField(default=0, verbose_name='highest_price', max_digits=10, decimal_places=2)),
                ('lowest_price', models.DecimalField(default=0, verbose_name='lowest_price', max_digits=10, decimal_places=2)),
                ('closing_price', models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2)),
                ('price_change', models.DecimalField(default=0, verbose_name='price_change', max_digits=10, decimal_places=2)),
                ('last_best_bid_price', models.DecimalField(default=0, verbose_name='last_best_bid_price', max_digits=10, decimal_places=2)),
                ('last_best_bid_volume', models.DecimalField(default=0, verbose_name='last_best_bid_volume', max_digits=15, decimal_places=0)),
                ('last_best_ask_price', models.DecimalField(default=0, verbose_name='last_best_ask_price', max_digits=10, decimal_places=2)),
                ('last_best_ask_volume', models.DecimalField(default=0, verbose_name='last_best_ask_volume', max_digits=15, decimal_places=0)),
                ('warrant_symbol', models.ForeignKey(related_name='twse_trading_warrant_list', verbose_name='warrant_symbol', to='core.Warrant_Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
