from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from core.utils import code_property

from ..channels import channels

CHANNEL_CHOICES = [
    ("email", _("E-mail")),
    ("callback", _("Callback")),
]


class Subscription(models.Model):
    """
    Channels:

    * `email` - e-mail will be sent to `user`
    * `callback` - the callback specified in `callback_code` will be called (for testing mostly).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=255)
    channel = models.CharField(
        max_length=max(len(key) for (key, label) in CHANNEL_CHOICES),
        default="email",
        choices=CHANNEL_CHOICES,
    )
    active = models.BooleanField(default=True)

    event_filter = models.ForeignKey(
        "core.Event",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Event filter"),
        help_text=_("When specified, only entries related to this event will match the subscription."),
    )
    job_category_filter = models.ForeignKey(
        "labour.JobCategory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Job category filter"),
        help_text=_("When specified, only entries related to this JobCategory will match the subscription."),
    )

    callback_code = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Callback function"),
        help_text=_(
            "Code path to a callback function. Only used when channel=callback. Eg. event_log.tests:test_callback."
        ),
    )

    callback = code_property("callback_code")

    def send_update_for_entry(self, entry):
        assert self.active

        if "background_tasks" in settings.INSTALLED_APPS:
            from ..tasks import subscription_send_update_for_entry

            subscription_send_update_for_entry.delay(self.id, entry.id)
        else:
            self._send_update_for_entry(entry)

    def _send_update_for_entry(self, entry):
        channels[self.channel].send_update_for_entry(self, entry)

    def clean(self):
        if self.callback_code and self.channel != "callback":
            raise ValidationError(_('The callback field must only be used when the channel is "callback".'))

    @property
    def recipient_name_and_email(self):
        full_name = self.user.get_full_name()
        if full_name:
            return f"{full_name} <{self.user.email}>"
        else:
            return self.user.email

    @classmethod
    def get_or_create_dummy(cls, entry_type=None, **kwargs):
        from core.models import Person

        from .entry_type_metadata import EntryTypeMetadata

        if entry_type is None:
            entry_type, unused = EntryTypeMetadata.get_or_create_dummy()
            entry_type = entry_type.name

        person, unused = Person.get_or_create_dummy()

        attrs = dict(
            entry_type=entry_type,
            user=person.user,
        )

        attrs.update(kwargs)

        return cls.objects.get_or_create(**attrs)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        index_together = [
            ("entry_type", "active"),
        ]
