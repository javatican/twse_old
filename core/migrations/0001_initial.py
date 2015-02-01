# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dealer_Trading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proprietary_buy', models.PositiveIntegerField(default=0, verbose_name='proprietary_buy')),
                ('proprietary_sell', models.PositiveIntegerField(default=0, verbose_name='proprietary_sell')),
                ('proprietary_diff', models.IntegerField(default=0, verbose_name='proprietary_diff')),
                ('hedge_buy', models.PositiveIntegerField(default=0, verbose_name='hedge_buy')),
                ('hedge_sell', models.PositiveIntegerField(default=0, verbose_name='hedge_sell')),
                ('hedge_diff', models.IntegerField(default=0, verbose_name='hedge_diff')),
                ('trading_date', models.DateField(auto_now_add=True, verbose_name='trading_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stock_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(default=b'', max_length=10, verbose_name='stock_symbol')),
                ('name', models.CharField(default=b'', max_length=20, verbose_name='stock_name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Warrant_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(default=b'', max_length=10, verbose_name='warrant_symbol')),
                ('name', models.CharField(default=b'', max_length=20, verbose_name='warrant_name')),
                ('target_stock', models.ForeignKey(related_name='warrant_item_list', verbose_name='target_stock', to='core.Stock_Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dealer_trading',
            name='stock_symbol',
            field=models.ForeignKey(related_name='dealer_trading_list', verbose_name='stock_symbol', to='core.Stock_Item', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dealer_trading',
            name='warrant_symbol',
            field=models.ForeignKey(related_name='dealer_trading_list2', verbose_name='warrant_symbol', to='core.Warrant_Item', null=True),
            preserve_default=True,
        ),
    ]
