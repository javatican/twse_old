# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150115_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_item',
            name='missing_info',
            field=models.BooleanField(default=True, verbose_name='missing_info'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='warrant_item',
            name='missing_info',
            field=models.BooleanField(default=True, verbose_name='missing_info'),
            preserve_default=True,
        ),
    ]
