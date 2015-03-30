# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20150320_0113'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_index_stats',
            name='day_d',
            field=models.DecimalField(null=True, verbose_name='day_d', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='day_k',
            field=models.DecimalField(null=True, verbose_name='day_k', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='half_avg',
            field=models.DecimalField(null=True, verbose_name='half_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='month_avg',
            field=models.DecimalField(null=True, verbose_name='month_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='month_d',
            field=models.DecimalField(null=True, verbose_name='month_d', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='month_k',
            field=models.DecimalField(null=True, verbose_name='month_k', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='quarter_avg',
            field=models.DecimalField(null=True, verbose_name='quarter_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='two_week_avg',
            field=models.DecimalField(null=True, verbose_name='two_week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='week_avg',
            field=models.DecimalField(null=True, verbose_name='week_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='week_d',
            field=models.DecimalField(null=True, verbose_name='week_d', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='week_k',
            field=models.DecimalField(null=True, verbose_name='week_k', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_index_stats',
            name='year_avg',
            field=models.DecimalField(null=True, verbose_name='year_avg', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
