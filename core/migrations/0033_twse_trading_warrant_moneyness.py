# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_twse_trading_warrant_not_converged'),
    ]

    operations = [
        migrations.AddField(
            model_name='twse_trading_warrant',
            name='moneyness',
            field=models.DecimalField(null=True, verbose_name='moneyness', max_digits=9, decimal_places=3),
            preserve_default=True,
        ),
    ]
