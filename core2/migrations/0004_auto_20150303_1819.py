# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core2', '0003_auto_20150302_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='gt_trading_warrant',
            name='target_stock_symbol',
            field=models.ForeignKey(related_name='gt_trading_warrant_list2', verbose_name='target_stock_symbol', to='core2.Gt_Stock_Item', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gt_trading_warrant',
            name='target_stock_trading',
            field=models.ForeignKey(related_name='gt_trading_warrant_list3', verbose_name='target_stock_trading', to='core2.Gt_Trading', null=True),
            preserve_default=True,
        ),
    ]
