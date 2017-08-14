# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-14 19:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import labour.models.signup_extras


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0028_auto_20170802_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignupExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('prior_experience', models.TextField(blank=True, help_text='Kerro tässä kentässä, jos sinulla on aiempaa kokemusta vastaavista tehtävistä tai muuta sellaista työkokemusta, josta arvioit olevan hyötyä hakemassasi tehtävässä.', verbose_name='Työkokemus')),
                ('shift_wishes', models.TextField(blank=True, help_text='Jos tiedät nyt jo, ettet pääse paikalle johonkin tiettyyn aikaan tai haluat osallistua johonkin tiettyyn ohjelmanumeroon, mainitse siitä tässä.', verbose_name='Työvuorotoiveet')),
                ('free_text', models.TextField(blank=True, help_text='Jos haluat sanoa hakemuksesi käsittelijöille jotain sellaista, jolle ei ole omaa kenttää yllä, käytä tätä kenttää.', verbose_name='Vapaa alue')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nippori2017_signup_extras', to='core.Event')),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='nippori2017_signup_extra', to='core.Person')),
            ],
            options={
                'abstract': False,
            },
            bases=(labour.models.signup_extras.SignupExtraMixin, models.Model),
        ),
    ]
