# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_warrant_item_trading_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twse_Index_Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('trade_volume', models.DecimalField(default=0, verbose_name='trade_volume', max_digits=15, decimal_places=0)),
                ('trade_transaction', models.DecimalField(default=0, verbose_name='trade_transaction', max_digits=15, decimal_places=0)),
                ('trade_value', models.DecimalField(default=0, verbose_name='trade_value', max_digits=15, decimal_places=0)),
                ('opening_price', models.DecimalField(default=0, verbose_name='opening_price', max_digits=10, decimal_places=2)),
                ('highest_price', models.DecimalField(default=0, verbose_name='highest_price', max_digits=10, decimal_places=2)),
                ('lowest_price', models.DecimalField(default=0, verbose_name='lowest_price', max_digits=10, decimal_places=2)),
                ('closing_price', models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2)),
                ('price_change', models.DecimalField(default=0, verbose_name='price_change', max_digits=10, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
