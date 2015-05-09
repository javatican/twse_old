# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_auto_20150504_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection_stock_item',
            name='has_warrant',
            field=models.BooleanField(default=False, verbose_name='has_warrant'),
            preserve_default=True,
        ),
    ]
