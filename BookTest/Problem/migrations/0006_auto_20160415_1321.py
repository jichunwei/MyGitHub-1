# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 05:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Problem', '0005_auto_20160415_1311'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Status',
        ),
        migrations.AddField(
            model_name='solve',
            name='xtype',
            field=models.CharField(blank=True, choices=[('0', 'unslove'), ('1', 'solve')], help_text='\u89e3\u51b3/\u672a\u89e3\u51b3', max_length=100),
        ),
    ]