# Generated by Django 2.1.8 on 2019-04-27 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0022_badge_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgeseventmeta',
            name='is_using_fuzzy_reissuance_hack',
        ),
    ]