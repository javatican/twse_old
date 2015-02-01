# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20150125_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading',
            name='last_best_ask_price',
            field=models.DecimalField(default=0, verbose_name='last_best_ask_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='last_best_ask_volume',
            field=models.DecimalField(default=0, verbose_name='last_best_ask_volume', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='last_best_bid_price',
            field=models.DecimalField(default=0, verbose_name='last_best_bid_price', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading',
            name='last_best_bid_volume',
            field=models.DecimalField(default=0, verbose_name='last_best_bid_volume', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
    ]
