# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20150201_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trading_Date',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('day_of_week', models.PositiveIntegerField(default=9, verbose_name='day_of_week')),
                ('is_future_delivery_day', models.BooleanField(default=False, verbose_name='is_future_delivery_day')),
                ('first_trading_day_of_month', models.BooleanField(default=False, verbose_name='first_trading_day_of_month')),
                ('last_trading_day_of_month', models.BooleanField(default=False, verbose_name='last_trading_day_of_month')),
                ('is_market_closed', models.BooleanField(default=False, verbose_name='is_market_closed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
