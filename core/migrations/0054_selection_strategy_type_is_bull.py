# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20150505_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='selection_strategy_type',
            name='is_bull',
            field=models.NullBooleanField(verbose_name='is_bull'),
            preserve_default=True,
        ),
    ]
