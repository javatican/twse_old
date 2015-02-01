# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_twse_trading_warrant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twse_trading',
            name='warrant_symbol',
        ),
        migrations.AlterUniqueTogether(
            name='twse_trading_warrant',
            unique_together=set([('warrant_symbol', 'trading_date')]),
        ),
    ]
