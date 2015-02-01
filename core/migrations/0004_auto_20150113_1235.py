# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_dealer_trading_downloaded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer_trading_downloaded',
            name='trading_date',
            field=models.DateField(unique=True, verbose_name='trading_date'),
            preserve_default=True,
        ),
    ]
