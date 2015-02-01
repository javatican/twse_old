# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cron_job_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dealer_Trading_Downloaded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trading_date', models.DateField(verbose_name='trading_date')),
                ('is_processed', models.BooleanField(default=False, verbose_name='is_processed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
