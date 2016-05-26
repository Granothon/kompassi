# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-29 16:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0007_remove_badgeseventmeta_badge_factory_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='badges.Batch', verbose_name='Printing batch'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='job_title',
            field=models.CharField(blank=True, default='', max_length=63, verbose_name='Job title'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Person', verbose_name='Person'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='personnel_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labour.PersonnelClass', verbose_name='Personnel class'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='printed_separately_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Printed separately at'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='revoked_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Revoked at'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AlterField(
            model_name='badgeseventmeta',
            name='badge_layout',
            field=models.CharField(choices=[(b'trad', 'Traditional'), (b'nick', 'Emphasize nick name')], default=b'trad', help_text='This controls how fields are grouped in the badge. Traditional: job title, firstname surname, nick. Emphasize nick name: first name or nick, surname or full name, job title.', max_length=4, verbose_name='Badgen asettelu'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
    ]