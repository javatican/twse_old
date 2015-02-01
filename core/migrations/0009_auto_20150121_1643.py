# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150119_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_item',
            name='data_available',
            field=models.BooleanField(default=False, verbose_name='data_available'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='data_available',
            field=models.BooleanField(default=False, verbose_name='data_available'),
            preserve_default=True,
        ),
    ]
