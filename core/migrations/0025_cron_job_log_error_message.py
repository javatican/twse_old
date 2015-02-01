# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20150131_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='cron_job_log',
            name='error_message',
            field=models.CharField(default=b'', max_length=120, verbose_name='cron_job_error_message'),
            preserve_default=True,
        ),
    ]
