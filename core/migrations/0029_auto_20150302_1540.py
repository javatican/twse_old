# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20150302_1531'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Twse_Summary_Price_Downloaded',
            new_name='Twse_Summary_Price_Processed',
        ),
        migrations.RenameModel(
            old_name='Twse_Trading_Downloaded',
            new_name='Twse_Trading_Processed',
        ),
    ]
