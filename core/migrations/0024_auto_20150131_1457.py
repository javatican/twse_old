# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20150131_1427'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='twse_trading',
            unique_together=set([('stock_symbol', 'trading_date')]),
        ),
    ]
