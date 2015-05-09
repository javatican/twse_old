# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_auto_20150505_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection_stock_item',
            name='volume_change',
            field=models.DecimalField(null=True, verbose_name='volume_change', max_digits=11, decimal_places=0),
            preserve_default=True,
        ),
    ]
