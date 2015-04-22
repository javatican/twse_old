# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core2', '0005_auto_20150311_1127'),
    ]

#modifiled by ryan for dealing with field rename
    operations = [
        migrations.RenameField(
            model_name='gt_market_highlight',
            old_name='closing_index',
            new_name='closing_price',
        ),
    ]
