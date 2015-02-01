# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150121_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='warrant_item',
            name='type_code',
            field=models.CharField(default=b'1', max_length=1, verbose_name='stock_type', choices=[(b'1', 'stock_type_1'), (b'2', 'stock_type_2')]),
            preserve_default=True,
        ),
    ]
