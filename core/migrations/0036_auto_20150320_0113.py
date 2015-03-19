# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_twse_index_stats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trading_date',
            name='trading_date',
            field=models.DateField(unique=True, verbose_name='trading_date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twse_index_stats',
            name='trading_date',
            field=models.DateField(unique=True, verbose_name='trading_date'),
            preserve_default=True,
        ),
    ]
