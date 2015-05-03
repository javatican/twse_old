# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_index_change_info_year_value_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='index_change_info',
            name='adx',
            field=models.DecimalField(null=True, verbose_name='adx', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='fourteen_day_d',
            field=models.DecimalField(null=True, verbose_name='fourteen_day_d', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='fourteen_day_k',
            field=models.DecimalField(null=True, verbose_name='fourteen_day_k', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='ndi14',
            field=models.DecimalField(null=True, verbose_name='ndi14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='ndm14',
            field=models.DecimalField(null=True, verbose_name='ndm14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='pdi14',
            field=models.DecimalField(null=True, verbose_name='pdi14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='pdm14',
            field=models.DecimalField(null=True, verbose_name='pdm14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='seventy_day_d',
            field=models.DecimalField(null=True, verbose_name='seventy_day_d', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='seventy_day_k',
            field=models.DecimalField(null=True, verbose_name='seventy_day_k', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='index_change_info',
            name='tr14',
            field=models.DecimalField(null=True, verbose_name='tr14', max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
    ]
