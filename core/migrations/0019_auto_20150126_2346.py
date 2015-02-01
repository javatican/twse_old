# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150126_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Index_Change_Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('closing_index', models.DecimalField(default=0, verbose_name='closing_index', max_digits=15, decimal_places=2)),
                ('change', models.DecimalField(default=0, verbose_name='change', max_digits=15, decimal_places=2)),
                ('change_in_percentage', models.DecimalField(default=0, verbose_name='change_in_percentage', max_digits=8, decimal_places=2)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Index_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100, verbose_name='index_name')),
                ('name_en', models.CharField(default=b'', max_length=100, verbose_name='index_name_en')),
                ('is_total_return_index', models.BooleanField(default=False, verbose_name='is_total_return_index')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Market_Summary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trade_value', models.DecimalField(default=0, verbose_name='trade_value', max_digits=17, decimal_places=0)),
                ('trade_volume', models.DecimalField(default=0, verbose_name='trade_volume', max_digits=17, decimal_places=0)),
                ('trade_transaction', models.DecimalField(default=0, verbose_name='trade_transaction', max_digits=17, decimal_places=0)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Market_Summary_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100, verbose_name='market_summary_type_name')),
                ('name_en', models.CharField(default=b'', max_length=100, verbose_name='market_summary_type_name_en')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stock_Up_Down_Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_up', models.PositiveIntegerField(default=0, verbose_name='total_up')),
                ('total_up_limit', models.PositiveIntegerField(default=0, verbose_name='total_up_limit')),
                ('stock_up', models.PositiveIntegerField(default=0, verbose_name='stock_up')),
                ('stock_up_limit', models.PositiveIntegerField(default=0, verbose_name='stock_up_limit')),
                ('total_down', models.PositiveIntegerField(default=0, verbose_name='total_down')),
                ('total_down_limit', models.PositiveIntegerField(default=0, verbose_name='total_down_limit')),
                ('stock_down', models.PositiveIntegerField(default=0, verbose_name='stock_down')),
                ('stock_down_limit', models.PositiveIntegerField(default=0, verbose_name='stock_down_limit')),
                ('total_unchange', models.PositiveIntegerField(default=0, verbose_name='total_unchange')),
                ('stock_unchange', models.PositiveIntegerField(default=0, verbose_name='stock_unchange')),
                ('total_unmatch', models.PositiveIntegerField(default=0, verbose_name='total_unmatch')),
                ('stock_unmatch', models.PositiveIntegerField(default=0, verbose_name='stock_unmatch')),
                ('total_na', models.PositiveIntegerField(default=0, verbose_name='total_na')),
                ('stock_na', models.PositiveIntegerField(default=0, verbose_name='stock_na')),
                ('trading_date', models.DateField(verbose_name='trading_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='market_summary',
            name='summary_type',
            field=models.ForeignKey(related_name='summary_list', verbose_name='summary_type', to='core.Market_Summary_Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='twse_index',
            field=models.ForeignKey(related_name='index_change_list', verbose_name='twse_index', to='core.Index_Item'),
            preserve_default=True,
        ),
    ]
