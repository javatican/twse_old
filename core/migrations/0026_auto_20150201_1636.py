# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_cron_job_log_error_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock_up_down_stats',
            name='trading_date',
            field=models.DateField(unique=True, verbose_name='trading_date'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='index_change_info',
            unique_together=set([('twse_index', 'trading_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='market_summary',
            unique_together=set([('summary_type', 'trading_date')]),
        ),
    ]
