# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20150421_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='index_change_info',
            name='half_avg',
            field=models.DecimalField(null=True, verbose_name='half_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='highest_price',
            field=models.DecimalField(default=0, verbose_name='highest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='lowest_price',
            field=models.DecimalField(default=0, verbose_name='lowest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='month_avg',
            field=models.DecimalField(null=True, verbose_name='month_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='opening_price',
            field=models.DecimalField(default=0, verbose_name='opening_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='quarter_avg',
            field=models.DecimalField(null=True, verbose_name='quarter_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='trade_value',
            field=models.DecimalField(default=0, verbose_name='trade_value', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='two_week_avg',
            field=models.DecimalField(null=True, verbose_name='two_week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='week_avg',
            field=models.DecimalField(null=True, verbose_name='week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='year_avg',
            field=models.DecimalField(null=True, verbose_name='year_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='change',
            field=models.DecimalField(default=0, verbose_name='change', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='closing_price',
            field=models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
