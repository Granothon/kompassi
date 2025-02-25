# Generated by Django 4.2.6 on 2023-11-03 19:56

import django.core.validators
import django.db.models.deletion
import localized_fields.fields.text_field
import localized_fields.mixins
import psqlextra.manager.manager
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forms", "0007_eventform_eventformresponse_globalform_and_more"),
        ("core", "0038_alter_person_discord_handle"),
        ("program_v2", "0002_emconcisen"),
    ]

    operations = [
        migrations.CreateModel(
            name="OfferForm",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "slug",
                    models.CharField(
                        help_text='Tekninen nimi eli "slug" näkyy URL-osoitteissa. Sallittuja merkkejä ovat pienet kirjaimet, numerot ja väliviiva. Teknistä nimeä ei voi muuttaa luomisen jälkeen.',
                        max_length=255,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Tekninen nimi saa sisältää vain pieniä kirjaimia, numeroita sekä väliviivoja.",
                                regex="[a-z0-9-]+",
                            )
                        ],
                        verbose_name="Tekninen nimi",
                    ),
                ),
                (
                    "short_description",
                    localized_fields.fields.text_field.LocalizedTextField(
                        blank=True,
                        default=dict,
                        help_text="Visible on the page that offers different kinds of forms.",
                        required=[],
                        verbose_name="short description",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="program_offer_forms", to="core.event"
                    ),
                ),
            ],
            options={
                "unique_together": {("event", "slug")},
            },
            bases=(localized_fields.mixins.AtomicSlugRetryMixin, models.Model),
            managers=[
                ("objects", psqlextra.manager.manager.PostgresManager()),
            ],
        ),
        migrations.CreateModel(
            name="OfferFormLanguage",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(max_length=2, verbose_name="language")),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="+", to="forms.eventform"
                    ),
                ),
                (
                    "offer_form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="languages", to="program_v2.offerform"
                    ),
                ),
            ],
        ),
    ]
