import logging
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.contrib import messages

from core.utils import horizontal_form_helper
from paikkala.views import (
    RelinquishView as BaseRelinquishView,
    ReservationView as BaseReservationView,
    InspectionView as BaseInspectionView,
)
from paikkala.excs import (
    BatchSizeOverflow,
    MaxTicketsPerUserReached,
    MaxTicketsReached,
    NoCapacity,
    NoRowCapacity,
    Unreservable,
    UserRequired,
)

from ..forms import ReservationForm
from ..helpers import programme_event_required
from ..models import Programme


logger = logging.getLogger('kompassi')


class PaikkalAdapterMixin:
    """
    Translates between Kompassi and Paikkala.
    """
    def get_context_data(self, **kwargs):
        """
        Kompassi `base.pug` template needs `event`.
        """
        context = super().get_context_data(**kwargs)
        context['event'] = self.kwargs['event']
        return context

    def get_programme(self):
        event = self.kwargs['event']
        programme_id = self.kwargs['programme_id']  # NOTE: programme.Programme, not paikkala.Program
        return Programme.objects.get(
            id=int(programme_id),
            category__event=event,
            is_using_paikkala=True,
            paikkala_program__isnull=False,
        )

    def get_success_url(self):
        return reverse('programme_profile_reservations_view')


def handle_errors(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # exc_info may only be called from inside exception handler
        # don't use logger.exception, it spams the admin
        try:
            return view_func(request, *args, **kwargs)
        except (MaxTicketsReached, MaxTicketsPerUserReached):
            message = _('You cannot reserve any more tickets for this programme.')
            logger.warning(message, exc_info=True)
        except BatchSizeOverflow:
            message = _('The size of your reservation exceeds the allowed maximum. Please try a smaller reservation.')
            logger.warning(message, exc_info=True)
        except Unreservable:
            message = _('This programme does not allow reservations at this time.')
            logger.warning(message, exc_info=True)
        except UserRequired:
            message = _('You need to log in before reserving tickets.')
            logger.warning(message, exc_info=True)
        except PermissionDenied:
            message = _('Permission denied.')
            logger.warning(message, exc_info=True)
        except (NoCapacity, NoRowCapacity):
            message = _("There isn't sufficient space for your reservation in the selected zone. Please try another zone.")
            logger.warning(message, exc_info=True)

        messages.error(request, message)
        return redirect(request.path)
    return wrapper


class InspectionView(PaikkalAdapterMixin, BaseInspectionView):
    template_name = 'paikkala_inspection_view.pug'
    require_same_user = True
    require_same_zone = True


class RelinquishView(PaikkalAdapterMixin, BaseRelinquishView):
    success_message_template = _('Successfully relinquished the seat reservation.')


class ReservationView(PaikkalAdapterMixin, BaseReservationView):
    success_message_template = _('Seats successfully reserved.')
    form_class = ReservationForm
    template_name = 'paikkala_reservation_view.pug'

    def get_object(self, queryset=None):
        """
        The `programme_event_required` decorator adds `event` to kwargs.
        `programme_id`, referring to `programme.Programme`, comes from the URL.
        Using these, resolve and inject the `pk`, referring to `paikkala.Program`.
        """
        programme = self.get_programme()
        self.kwargs['pk'] = programme.paikkala_program_id
        return super().get_object(queryset)


    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.helper = horizontal_form_helper()
        form.helper.form_tag = False
        return form


paikkala_inspection_view = login_required(programme_event_required(InspectionView.as_view()))
paikkala_relinquish_view = login_required(programme_event_required(handle_errors(RelinquishView.as_view())))
paikkala_reservation_view = login_required(programme_event_required(handle_errors(ReservationView.as_view())))
