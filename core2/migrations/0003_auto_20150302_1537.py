# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core2', '0002_auto_20150302_1534'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Gt_Summary_Price_Downloaded',
            new_name='Gt_Summary_Price_Processed',
        ),
        migrations.RenameModel(
            old_name='Gt_Trading_Downloaded',
            new_name='Gt_Trading_Processed',
        ),
    ]
