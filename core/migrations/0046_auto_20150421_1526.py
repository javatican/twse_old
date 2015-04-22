# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20150421_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='index_change_info',
            name='change',
            field=models.DecimalField(null=True, verbose_name='change', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='change_in_percentage',
            field=models.DecimalField(null=True, verbose_name='change_in_percentage', max_digits=8, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='closing_price',
            field=models.DecimalField(null=True, verbose_name='closing_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='highest_price',
            field=models.DecimalField(null=True, verbose_name='highest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='lowest_price',
            field=models.DecimalField(null=True, verbose_name='lowest_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='opening_price',
            field=models.DecimalField(null=True, verbose_name='opening_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='index_change_info',
            name='trade_value',
            field=models.DecimalField(null=True, verbose_name='trade_value', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
    ]
