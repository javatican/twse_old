# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20150406_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwseTradingStrategy',
            fields=[
                ('trading', models.OneToOneField(primary_key=True, serialize=False, to='core.Twse_Trading')),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('fourteen_day_k', models.DecimalField(null=True, verbose_name='fourteen_day_k', max_digits=6, decimal_places=2)),
                ('fourteen_day_d', models.DecimalField(null=True, verbose_name='fourteen_day_d', max_digits=6, decimal_places=2)),
                ('seventy_day_k', models.DecimalField(null=True, verbose_name='seventy_day_k', max_digits=6, decimal_places=2)),
                ('seventy_day_d', models.DecimalField(null=True, verbose_name='seventy_day_d', max_digits=6, decimal_places=2)),
                ('stock_symbol', models.ForeignKey(related_name='twse_trading_so_list', verbose_name='stock_symbol', to='core.Stock_Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
