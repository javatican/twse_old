# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150125_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twse_Price_Downloaded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(unique=True, verbose_name='trading_date')),
                ('is_processed', models.BooleanField(default=False, verbose_name='is_processed')),
                ('data_available', models.BooleanField(default=True, verbose_name='data_available')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
