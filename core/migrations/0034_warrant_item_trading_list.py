# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_twse_trading_warrant_moneyness'),
    ]

    operations = [
        migrations.AddField(
            model_name='warrant_item',
            name='trading_list',
            field=models.TextField(null=True, verbose_name='trading_list'),
            preserve_default=True,
        ),
    ]
