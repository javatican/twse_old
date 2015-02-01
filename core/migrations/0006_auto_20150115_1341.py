# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_dealer_trading_downloaded_data_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer_trading',
            name='trading_date',
            field=models.DateField(verbose_name='trading_date'),
            preserve_default=True,
        ),
    ]
