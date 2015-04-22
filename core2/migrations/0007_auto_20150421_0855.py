# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core2', '0006_auto_20150421_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='gt_market_highlight',
            name='half_avg',
            field=models.DecimalField(null=True, verbose_name='half_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='highest_price',
            field=models.DecimalField(default=0, verbose_name='highest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='lowest_price',
            field=models.DecimalField(default=0, verbose_name='lowest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='month_avg',
            field=models.DecimalField(null=True, verbose_name='month_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='opening_price',
            field=models.DecimalField(default=0, verbose_name='opening_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='quarter_avg',
            field=models.DecimalField(null=True, verbose_name='quarter_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='two_week_avg',
            field=models.DecimalField(null=True, verbose_name='two_week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='week_avg',
            field=models.DecimalField(null=True, verbose_name='week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_market_highlight',
            name='year_avg',
            field=models.DecimalField(null=True, verbose_name='year_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gt_market_highlight',
            name='change',
            field=models.DecimalField(default=0, verbose_name='change', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gt_market_highlight',
            name='closing_price',
            field=models.DecimalField(default=0, verbose_name='closing_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
