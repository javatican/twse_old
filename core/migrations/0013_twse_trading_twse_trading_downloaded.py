# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150124_1820'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twse_Trading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_diff', models.IntegerField(default=0, verbose_name='total_diff')),
                ('fi_buy', models.PositiveIntegerField(default=0, verbose_name='fi_buy')),
                ('fi_sell', models.PositiveIntegerField(default=0, verbose_name='fi_sell')),
                ('fi_diff', models.IntegerField(default=0, verbose_name='fi_diff')),
                ('sit_buy', models.PositiveIntegerField(default=0, verbose_name='sit_buy')),
                ('sit_sell', models.PositiveIntegerField(default=0, verbose_name='sit_sell')),
                ('sit_diff', models.IntegerField(default=0, verbose_name='sit_diff')),
                ('proprietary_buy', models.PositiveIntegerField(default=0, verbose_name='proprietary_buy')),
                ('proprietary_sell', models.PositiveIntegerField(default=0, verbose_name='proprietary_sell')),
                ('proprietary_diff', models.IntegerField(default=0, verbose_name='proprietary_diff')),
                ('hedge_buy', models.PositiveIntegerField(default=0, verbose_name='hedge_buy')),
                ('hedge_sell', models.PositiveIntegerField(default=0, verbose_name='hedge_sell')),
                ('hedge_diff', models.IntegerField(default=0, verbose_name='hedge_diff')),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('stock_symbol', models.ForeignKey(related_name='twse_trading_list', verbose_name='stock_symbol', to='core.Stock_Item', null=True)),
                ('warrant_symbol', models.ForeignKey(related_name='twse_trading_list2', verbose_name='warrant_symbol', to='core.Warrant_Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Twse_Trading_Downloaded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(unique=True, verbose_name='trading_date')),
                ('is_processed', models.BooleanField(default=False, verbose_name='is_processed')),
                ('data_available', models.BooleanField(default=True, verbose_name='data_available')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
