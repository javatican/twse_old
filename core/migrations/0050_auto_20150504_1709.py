# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20150427_2314'),
    ]

    operations = [
        migrations.CreateModel(
            name='Selection_Stock_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('stock_symbol', models.ForeignKey(related_name='selection_list2', verbose_name='stock_symbol', to='core.Stock_Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Selection_Strategy_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(default=b'', max_length=50, verbose_name='strategy_symbol')),
                ('name', models.CharField(default=b'', max_length=100, verbose_name='strategy_name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='selection_stock_item',
            name='strategy_type',
            field=models.ForeignKey(related_name='selection_list', verbose_name='strategy_type', to='core.Selection_Strategy_Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selection_stock_item',
            name='trading',
            field=models.ForeignKey(related_name='selection_list3', verbose_name='trading', to='core.Twse_Trading'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_trading_strategy',
            name='stock_symbol',
            field=models.ForeignKey(related_name='twse_trading_strat_list', verbose_name='stock_symbol', to='core.Stock_Item'),
            preserve_default=True,
        ),
    ]
