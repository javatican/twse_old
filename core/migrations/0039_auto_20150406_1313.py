# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20150330_1646'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twse_trading',
            name='day_d',
        ),
        migrations.RemoveField(
            model_name='twse_trading',
            name='day_k',
        ),
        migrations.RemoveField(
            model_name='twse_trading',
            name='month_d',
        ),
        migrations.RemoveField(
            model_name='twse_trading',
            name='month_k',
        ),
        migrations.RemoveField(
            model_name='twse_trading',
            name='week_d',
        ),
        migrations.RemoveField(
            model_name='twse_trading',
            name='week_k',
        ),
    ]
