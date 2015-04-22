# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20150410_1241'),
    ]
#modifiled by ryan for dealing with field rename
    operations = [
        migrations.RenameField(
            model_name='index_change_info',
            old_name='closing_index',
            new_name='closing_price',
        ),
        migrations.AddField(
            model_name='index_item',
            name='wearn_symbol',
            field=models.CharField(max_length=15, null=True, verbose_name='wearn_symbol'),
            preserve_default=True,
        ),
    ]
