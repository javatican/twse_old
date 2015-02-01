# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150113_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='dealer_trading_downloaded',
            name='data_available',
            field=models.BooleanField(default=True, verbose_name='data_available'),
            preserve_default=True,
        ),
    ]
