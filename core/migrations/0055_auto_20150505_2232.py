# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_selection_strategy_type_is_bull'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection_stock_item',
            name='performance_10day',
            field=models.DecimalField(null=True, verbose_name='performance_10day', max_digits=7, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selection_stock_item',
            name='performance_20day',
            field=models.DecimalField(null=True, verbose_name='performance_20day', max_digits=7, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selection_stock_item',
            name='performance_3day',
            field=models.DecimalField(null=True, verbose_name='performance_3day', max_digits=7, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selection_stock_item',
            name='performance_5day',
            field=models.DecimalField(null=True, verbose_name='performance_5day', max_digits=7, decimal_places=1),
            preserve_default=True,
        ),
    ]
