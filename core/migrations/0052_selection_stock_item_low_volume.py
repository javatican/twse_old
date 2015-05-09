# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_selection_stock_item_has_warrant'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection_stock_item',
            name='low_volume',
            field=models.BooleanField(default=True, verbose_name='low_volume'),
            preserve_default=True,
        ),
    ]
