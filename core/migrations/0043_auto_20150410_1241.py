# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20150407_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='ndm14',
            field=models.DecimalField(null=True, verbose_name='ndm14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='pdm14',
            field=models.DecimalField(null=True, verbose_name='pdm14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='tr14',
            field=models.DecimalField(null=True, verbose_name='tr14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
    ]
