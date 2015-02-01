# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_warrant_item_type_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_item',
            name='etf_target',
            field=models.CharField(default=b'', max_length=100, verbose_name='etf_target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stock_item',
            name='is_etf',
            field=models.BooleanField(default=False, verbose_name='is_etf'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stock_item',
            name='name',
            field=models.CharField(default=b'', max_length=100, verbose_name='stock_name'),
            preserve_default=True,
        ),
    ]
