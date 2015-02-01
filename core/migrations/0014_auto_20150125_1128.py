# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_twse_trading_twse_trading_downloaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealer_trading',
            name='stock_symbol',
        ),
        migrations.RemoveField(
            model_name='dealer_trading',
            name='warrant_symbol',
        ),
        migrations.DeleteModel(
            name='Dealer_Trading',
        ),
        migrations.DeleteModel(
            name='Dealer_Trading_Downloaded',
        ),
    ]
