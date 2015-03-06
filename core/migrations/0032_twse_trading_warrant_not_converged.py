# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20150304_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='not_converged',
            field=models.NullBooleanField(verbose_name='not_converged'),
            preserve_default=True,
        ),
    ]
