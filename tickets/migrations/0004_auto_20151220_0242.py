# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-20 02:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_auto_20151219_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.Category'),
        ),
        migrations.AlterField(
            model_name='show',
            name='long_description',
            field=models.TextField(blank=True, help_text=b'Shows up on the detail page, this field is written in Markdown. (See <a href="http://www.darkcoding.net/software/markdown-quick-reference/">Markdown reference</a> for reference.'),
        ),
    ]
