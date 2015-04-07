# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20150406_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='adx',
            field=models.DecimalField(null=True, verbose_name='adx', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='ndi14',
            field=models.DecimalField(null=True, verbose_name='ndi14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_strategy',
            name='pdi14',
            field=models.DecimalField(null=True, verbose_name='pdi14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
    ]
