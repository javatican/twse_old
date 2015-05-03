# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20150423_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='index_change_info',
            name='year_value_avg',
            field=models.DecimalField(null=True, verbose_name='year_value_avg', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
    ]
