import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from localized_fields.fields import LocalizedCharField
from localized_fields.models import LocalizedModel

from core.models import ContactEmailMixin, EventMetaBase, contact_email_validator

from .consts import TICKETS_VIEW_VERSION_CHOICES

logger = logging.getLogger("kompassi")


class TicketsEventMeta(ContactEmailMixin, EventMetaBase, LocalizedModel):
    due_days = models.IntegerField(
        verbose_name=_("Payment due (days)"),
        default=14,
    )

    ticket_sales_starts = models.DateTimeField(
        verbose_name=_("Ticket sales starts"),
        null=True,
        blank=True,
    )

    ticket_sales_ends = models.DateTimeField(
        verbose_name=_("Ticket sales ends"),
        null=True,
        blank=True,
    )

    reference_number_template = models.CharField(
        max_length=31,
        default="{:04d}",
        verbose_name=_("Reference number template"),
        help_text=_("Uses Python .format() string formatting."),
    )

    contact_email = models.CharField(
        max_length=255,
        validators=[
            contact_email_validator,
        ],
        verbose_name=_("Contact e-mail address (with description)"),
        help_text=_("Format: Fooevent Ticket Sales &lt;tickets@fooevent.example.com&gt;"),
        blank=True,
    )

    ticket_spam_email = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Monitoring e-mail address"),
        help_text=_("If set, all tickets-related e-mail messages will be also sent to this e-mail address."),
    )

    reservation_seconds = models.IntegerField(
        verbose_name=_("Reservation period (seconds)"),
        help_text=_(
            "This is how long the customer has after confirmation to complete the payment. NOTE: Currently unimplemented."
        ),
        default=1800,
    )

    ticket_free_text = models.TextField(
        blank=True,
        verbose_name=_("E-ticket text"),
        help_text=_("This text will be printed in the electronic ticket."),
    )

    front_page_text = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Front page text"),
        help_text=_("This text will be shown on the front page of the web shop."),
    )

    print_logo_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Logo path"),
        help_text=_("The file system path to a logo that will be printed on the electronic ticket."),
    )

    print_logo_width_mm = models.IntegerField(
        default=0,
        verbose_name=_("Logo width (mm)"),
        help_text=_(
            "The width of the logo to be printed on electronic tickets, in millimeters. Roughly 40 mm recommended."
        ),
    )

    print_logo_height_mm = models.IntegerField(
        default=0,
        verbose_name=_("Logo height (mm)"),
        help_text=_(
            "The height of the logo to be printed on electronic tickets, in millimeters. Roughly 20 mm recommended."
        ),
    )

    receipt_footer = models.CharField(
        blank=True,
        default="",
        max_length=1023,
        verbose_name=_("Receipt footer"),
        help_text=_(
            "This text will be printed in the footer of printed receipts (for mail orders). Entering contact information here is recommended."
        ),
    )

    pos_access_group = models.ForeignKey(
        "auth.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("POS access group"),
        help_text=_(
            "Members of this group are granted access to the ticket exchange view without being ticket admins."
        ),
        related_name="as_pos_access_group_for",
    )

    accommodation_access_group = models.ForeignKey(
        "auth.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Accommodation access group"),
        help_text=_(
            "Members of this group are granted access to the accommodation onboarding view without being ticket admins."
        ),
        related_name="as_accommodation_access_group_for",
    )

    terms_and_conditions_url = LocalizedCharField(
        blank=True,
        default=dict,
        max_length=1023,
        verbose_name=_("Terms and conditions URL"),
        help_text=_("If set, customers will be required to indicate acceptance to finish order."),
    )

    max_count_per_product = models.SmallIntegerField(blank=True, default=99)

    tickets_view_version = models.CharField(
        max_length=max(len(key) for (key, _) in TICKETS_VIEW_VERSION_CHOICES),
        choices=TICKETS_VIEW_VERSION_CHOICES,
        default=TICKETS_VIEW_VERSION_CHOICES[0][0],
        verbose_name=_("Tickets view version"),
    )

    def __str__(self):
        return self.event.name

    @property
    def print_logo_size_cm(self):
        return (self.print_logo_width_mm / 10.0, self.print_logo_height_mm / 10.0)

    @property
    def is_ticket_sales_open(self):
        t = timezone.now()

        # Starting date must be set for the ticket sales to be considered open
        if not self.ticket_sales_starts:
            return False

        # Starting date must be in the past for the ticket sales to be considered open
        elif self.ticket_sales_starts > t:
            return False

        # If there is an ending date, it must not have been passed yet
        elif self.ticket_sales_ends:
            return t <= self.ticket_sales_ends

        else:
            return True

    @classmethod
    def get_or_create_dummy(cls):
        from django.contrib.auth.models import Group

        from core.models import Event

        group, unused = Group.objects.get_or_create(name="Dummy ticket admin group")
        event, unused = Event.get_or_create_dummy()
        return cls.objects.get_or_create(event=event, defaults=dict(admin_group=group))

    def is_user_allowed_pos_access(self, user):
        if self.is_user_admin(user):
            return True

        return self.pos_access_group and self.is_user_in_group(user, self.pos_access_group)

    def is_user_allowed_accommodation_access(self, user):
        if self.is_user_admin(user):
            return True

        return self.pos_access_group and self.is_user_in_group(user, self.accommodation_access_group)

    class Meta:
        verbose_name = _("ticket sales settings for event")
        verbose_name_plural = _("ticket sales settings for events")
