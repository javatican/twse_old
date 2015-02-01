# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cron_Job_Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=48, verbose_name='cron_job_title')),
                ('exec_time', models.DateTimeField(auto_now_add=True, verbose_name='cron_job_exec_time')),
                ('status_code', models.CharField(default=b'1', max_length=1, verbose_name='cron_job_status', choices=[(b'1', 'cron_job_success'), (b'2', 'cron_job_failed')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
