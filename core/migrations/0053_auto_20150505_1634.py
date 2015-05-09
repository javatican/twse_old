# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_selection_stock_item_low_volume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selection_stock_item',
            name='has_warrant',
            field=models.NullBooleanField(verbose_name='has_warrant'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='selection_stock_item',
            name='low_volume',
            field=models.NullBooleanField(verbose_name='low_volume'),
            preserve_default=True,
        ),
    ]
