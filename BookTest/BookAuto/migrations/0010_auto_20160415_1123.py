# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 03:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BookAuto', '0009_auto_20160414_0041'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'verbose_name_plural': '\u4f5c\u8005'},
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'verbose_name_plural': '\u4e66\u7c4d'},
        ),
    ]
