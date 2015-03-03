# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20150302_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='target_stock_symbol',
            field=models.ForeignKey(related_name='twse_trading_warrant_list2', verbose_name='target_stock_symbol', to='core.Stock_Item', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='target_stock_trading',
            field=models.ForeignKey(related_name='twse_trading_warrant_list3', verbose_name='target_stock_trading', to='core.Twse_Trading', null=True),
            preserve_default=True,
        ),
    ]
