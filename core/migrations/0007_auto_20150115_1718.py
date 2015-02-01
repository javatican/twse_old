# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150115_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_item',
            name='market_category',
            field=models.CharField(default=b'', max_length=50, verbose_name='market_category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='notes',
            field=models.CharField(default=b'', max_length=100, verbose_name='notes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='short_name',
            field=models.CharField(default=b'', max_length=20, verbose_name='stock_short_name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='type_code',
            field=models.CharField(default=b'1', max_length=1, verbose_name='stock_type', choices=[(b'1', 'stock_type_1'), (b'2', 'stock_type_2')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='classification',
            field=models.CharField(default=1, max_length=1, verbose_name='classification', choices=[(b'1', 'call'), (b'2', 'put')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='exercise_ratio',
            field=models.PositiveIntegerField(default=0, verbose_name='exercise_ratio'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='exercise_style',
            field=models.CharField(default=1, max_length=1, verbose_name='exercise_style', choices=[(b'1', 'European'), (b'2', 'American')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='expiration_date',
            field=models.DateField(null=True, verbose_name='expiration_date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='issued_volume',
            field=models.PositiveIntegerField(default=0, verbose_name='issued_volume'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='issuer',
            field=models.CharField(default=b'', max_length=20, verbose_name='issuer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='last_trading_date',
            field=models.DateField(null=True, verbose_name='last_trading_date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='listed_date',
            field=models.DateField(null=True, verbose_name='listed_date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='strike_price',
            field=models.DecimalField(default=0, verbose_name='strike_price', max_digits=8, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='target_symbol',
            field=models.CharField(default=b'', max_length=10, verbose_name='target_symbol'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stock_item',
            name='name',
            field=models.CharField(default=b'', max_length=50, verbose_name='stock_name'),
            preserve_default=True,
        ),
    ]
