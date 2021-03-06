# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 16:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text=b'Shows up on pages.', max_length=50)),
                ('slug', models.SlugField(help_text=b'Will be used in class names, so you can style categories differently.')),
                ('sort', models.IntegerField(help_text=b'Low to high, sorts the sidebar.')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField(default=datetime.time(19, 0))),
                ('maximum_sell', models.PositiveIntegerField(default=80, help_text=b'The maximum number of tickets we will allow to be reserved.')),
                ('hours_til_close', models.IntegerField(default=2, help_text=b"Hours before 'time' that we will stop reservations being made.")),
            ],
            options={
                'verbose_name': 'Occurrence',
                'verbose_name_plural': 'Occurrences',
            },
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(blank=True, help_text=b'Used in the URL of the detail page, leave blank to auto-generate.')),
                ('location', models.CharField(default=b'New Theatre', help_text=b'Will show up alongside show, you can hide this with CSS if needed.', max_length=30)),
                ('description', models.TextField(help_text=b'A short description, one paragraph only.')),
                ('long_description', models.TextField(blank=True, help_text=b'Shows up on the detail page, this field is written in Markdown. (See <a href="http://www.darkcoding.net/software/markdown-quick-reference/">http://www.darkcoding.net/software/markdown-quick-reference/</a> for reference.')),
                ('poster', models.ImageField(blank=True, help_text=b'Upload a large image, we will automatically create smaller versions to use.', null=True, upload_to=b'posters')),
                ('poster_wall', models.ImageField(blank=True, null=True, upload_to=b'posters')),
                ('poster_page', models.ImageField(blank=True, null=True, upload_to=b'posters')),
                ('poster_tiny', models.ImageField(blank=True, null=True, upload_to=b'posters')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.category')),
            ],
            options={
                'verbose_name': 'Show',
                'verbose_name_plural': 'Shows',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.DateTimeField(auto_now=True)),
                ('person_name', models.CharField(max_length=80)),
                ('email_address', models.EmailField(max_length=80)),
                ('quantity', models.IntegerField(default=1)),
                ('cancelled', models.BooleanField(default=False)),
                ('unique_code', models.CharField(max_length=16)),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.Occurrence')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
            },
        ),
        migrations.AddField(
            model_name='occurrence',
            name='show',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.Show'),
        ),
    ]
