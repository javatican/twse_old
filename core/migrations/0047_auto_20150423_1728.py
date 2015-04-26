# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20150421_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_index_stats',
            name='year_value_avg',
            field=models.DecimalField(null=True, verbose_name='year_value_avg', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='year_volume_avg',
            field=models.DecimalField(null=True, verbose_name='year_volume_avg', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
    ]
