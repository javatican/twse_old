# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150126_2346'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Twse_Price_Downloaded',
            new_name='Twse_Summary_Price_Downloaded',
        ),
    ]
