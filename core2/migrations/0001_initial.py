# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gt_Market_Highlight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('listed_companies', models.PositiveIntegerField(default=0, verbose_name='listed_companies')),
                ('capitals', models.DecimalField(default=0, verbose_name='capitals', max_digits=17, decimal_places=0)),
                ('market_capitalization', models.DecimalField(default=0, verbose_name='market_capitalization', max_digits=17, decimal_places=0)),
                ('trade_value', models.DecimalField(default=0, verbose_name='trade_value', max_digits=17, decimal_places=0)),
                ('trade_volume', models.DecimalField(default=0, verbose_name='trade_volume', max_digits=17, decimal_places=0)),
                ('closing_index', models.DecimalField(default=0, verbose_name='closing_index', max_digits=15, decimal_places=2)),
                ('change', models.DecimalField(default=0, verbose_name='change', max_digits=15, decimal_places=2)),
                ('change_in_percentage', models.DecimalField(default=0, verbose_name='change_in_percentage', max_digits=8, decimal_places=2)),
                ('stock_up', models.PositiveIntegerField(default=0, verbose_name='stock_up')),
                ('stock_up_limit', models.PositiveIntegerField(default=0, verbose_name='stock_up_limit')),
                ('stock_down', models.PositiveIntegerField(default=0, verbose_name='stock_down')),
                ('stock_down_limit', models.PositiveIntegerField(default=0, verbose_name='stock_down_limit')),
                ('stock_unchange', models.PositiveIntegerField(default=0, verbose_name='stock_unchange')),
                ('stock_unmatch', models.PositiveIntegerField(default=0, verbose_name='stock_unmatch')),
                ('trading_date', models.DateField(unique=True, verbose_name='trading_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gt_Market_Summary',
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
            name='Gt_Market_Summary_Type',
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
            name='Gt_Stock_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(default=b'', max_length=10, verbose_name='stock_symbol')),
                ('short_name', models.CharField(default=b'', max_length=20, verbose_name='stock_short_name')),
                ('name', models.CharField(default=b'', max_length=100, verbose_name='stock_name')),
                ('type_code', models.CharField(default=b'2', max_length=1, verbose_name='stock_type', choices=[(b'1', 'stock_type_1'), (b'2', 'stock_type_2')])),
                ('market_category', models.CharField(default=b'', max_length=50, verbose_name='market_category')),
                ('notes', models.CharField(default=b'', max_length=100, verbose_name='notes')),
                ('data_ok', models.BooleanField(default=False, verbose_name='data_ok')),
                ('data_downloaded', models.BooleanField(default=False, verbose_name='data_downloaded')),
                ('parsing_error', models.BooleanField(default=False, verbose_name='parsing_error')),
                ('is_etf', models.BooleanField(default=False, verbose_name='is_etf')),
                ('etf_target', models.CharField(default=b'', max_length=100, verbose_name='etf_target')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gt_Summary_Price_Downloaded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(unique=True, verbose_name='trading_date')),
                ('summary_processed', models.BooleanField(default=False, verbose_name='summary_processed')),
                ('highlight_processed', models.BooleanField(default=False, verbose_name='highlight_processed')),
                ('price_processed', models.BooleanField(default=False, verbose_name='price_processed')),
                ('data_available', models.BooleanField(default=True, verbose_name='data_available')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gt_Trading',
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
                ('average_price', models.DecimalField(default=0, verbose_name='average_price', max_digits=10, decimal_places=2)),
                ('closing_price', models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2)),
                ('price_change', models.DecimalField(default=0, verbose_name='price_change', max_digits=10, decimal_places=2)),
                ('last_best_bid_price', models.DecimalField(default=0, verbose_name='last_best_bid_price', max_digits=10, decimal_places=2)),
                ('last_best_ask_price', models.DecimalField(default=0, verbose_name='last_best_ask_price', max_digits=10, decimal_places=2)),
                ('stock_symbol', models.ForeignKey(related_name='gt_trading_list', verbose_name='stock_symbol', to='core2.Gt_Stock_Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gt_Trading_Downloaded',
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
        migrations.CreateModel(
            name='Gt_Trading_Warrant',
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gt_Warrant_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('symbol', models.CharField(default=b'', max_length=10, verbose_name='warrant_symbol')),
                ('name', models.CharField(default=b'', max_length=20, verbose_name='warrant_name')),
                ('target_symbol', models.CharField(default=b'', max_length=10, verbose_name='target_symbol')),
                ('exercise_style', models.CharField(default=1, max_length=1, verbose_name='exercise_style', choices=[(b'1', 'European'), (b'2', 'American')])),
                ('classification', models.CharField(default=1, max_length=1, verbose_name='classification', choices=[(b'1', 'call'), (b'2', 'put')])),
                ('issuer', models.CharField(default=b'', max_length=20, verbose_name='issuer')),
                ('listed_date', models.DateField(null=True, verbose_name='listed_date')),
                ('last_trading_date', models.DateField(null=True, verbose_name='last_trading_date')),
                ('expiration_date', models.DateField(null=True, verbose_name='expiration_date')),
                ('issued_volume', models.PositiveIntegerField(default=0, verbose_name='issued_volume')),
                ('exercise_ratio', models.PositiveIntegerField(default=0, verbose_name='exercise_ratio')),
                ('strike_price', models.DecimalField(default=0, verbose_name='strike_price', max_digits=8, decimal_places=2)),
                ('data_ok', models.BooleanField(default=False, verbose_name='data_ok')),
                ('data_downloaded', models.BooleanField(default=False, verbose_name='data_downloaded')),
                ('parsing_error', models.BooleanField(default=False, verbose_name='parsing_error')),
                ('type_code', models.CharField(default=b'2', max_length=1, verbose_name='stock_type', choices=[(b'1', 'stock_type_1'), (b'2', 'stock_type_2')])),
                ('target_stock', models.ForeignKey(related_name='warrant_item_list', verbose_name='target_stock', to='core2.Gt_Stock_Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gt_trading_warrant',
            name='warrant_symbol',
            field=models.ForeignKey(related_name='gt_trading_warrant_list', verbose_name='warrant_symbol', to='core2.Gt_Warrant_Item', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gt_trading_warrant',
            unique_together=set([('warrant_symbol', 'trading_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='gt_trading',
            unique_together=set([('stock_symbol', 'trading_date')]),
        ),
        migrations.AddField(
            model_name='gt_market_summary',
            name='summary_type',
            field=models.ForeignKey(related_name='summary_list', verbose_name='summary_type', to='core2.Gt_Market_Summary_Type'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gt_market_summary',
            unique_together=set([('summary_type', 'trading_date')]),
        ),
    ]
