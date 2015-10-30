# encoding: utf-8

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods

from api.utils import api_view, api_login_required, handle_api_errors
from core.helpers import person_required
from core.models import Person
from core.utils import groupby_strict, url

from .models import Privilege, EmailAliasDomain, EmailAlias, SMTPServer, SMTPPassword
from .helpers import access_admin_required


@person_required
def access_profile_privileges_view(request):
    person = request.user.person

    vars = dict(
        granted_privileges=person.granted_privileges.all(),
        potential_privileges=Privilege.get_potential_privileges(person),
    )

    return render(request, 'access_profile_privileges_view.jade', vars)


@person_required
@require_POST
def access_profile_request_privilege_view(request, privilege_slug):
    if not request.user.person.is_email_verified:
        messages.error(request, u'Käyttöoikeuden pyytäminen edellyttää vahvistettua sähköpostiosoitetta.')
        return redirect('access_profile_privileges_view')

    # People belonging to both Hitpoint and Tracon concoms were getting MultipleObjectsReturned here.
    # Cannot use get_object_or_404 due to the same object being returned multiple times via multiple groups.
    # get_object_or_404 uses .get which has no way to provide .distinct() from outside.
    privilege = Privilege.objects.filter(
        slug=privilege_slug,
        group_privileges__group__in=request.user.groups.all(),
    ).first()
    if privilege is None:
        raise Http404('Privilege not found')

    privilege.grant(request.user.person)

    if privilege.request_success_message:
        success_message = privilege.request_success_message
    else:
        success_message = u'Käyttöoikeuden pyytäminen onnistui.'

    messages.success(request, success_message)
    return redirect('access_profile_privileges_view')


@person_required
@require_http_methods(['GET', 'POST'])
def access_profile_aliases_view(request):
    person = request.user.person

    if request.method == 'POST':
        domain = get_object_or_404(EmailAliasDomain,
            domain_name=request.POST.get('create_new_password_for_domain'),
            emailaliastype__email_aliases__person=request.user.person,
        )

        newly_created_password, unused = SMTPPassword.create_for_domain_and_person(domain, request.user.person)
    else:
        newly_created_password = None

    aliases_by_domain = [
        (
            domain,
            SMTPServer.objects.filter(domains=domain).exists(),
            SMTPPassword.objects.filter(person=request.user.person, smtp_server__domains=domain),
            aliases,
        )
        for (domain, aliases) in groupby_strict(person.email_aliases.all(), lambda alias: alias.domain)
    ]

    vars = dict(
        aliases_by_domain=aliases_by_domain,
        newly_created_password=newly_created_password,
        person=person,
    )

    return render(request, 'access_profile_aliases_view.jade', vars)


def access_profile_menu_items(request):
    privileges_url = reverse('access_profile_privileges_view')
    privileges_active = request.path.startswith(privileges_url)
    privileges_text = u"Käyttöoikeudet"

    items = [
        (privileges_active, privileges_url, privileges_text),
    ]

    try:
        aliases_visible = request.user.person.email_aliases.exists()
    except Person.DoesNotExist:
        aliases_visible = False

    if aliases_visible:
        aliases_url = reverse('access_profile_aliases_view')
        aliases_active = request.path == aliases_url
        aliases_text = u'Sähköpostialiakset'

        items.append((aliases_active, aliases_url, aliases_text))

    return items

@handle_api_errors
@api_login_required
def access_admin_aliases_api(request, domain_name):
    domain = get_object_or_404(EmailAliasDomain, domain_name=domain_name)

    lines = []

    for person in Person.objects.filter(email_aliases__domain=domain).distinct():
        lines.append(u'# {name}'.format(name=person.full_name))

        for alias in person.email_aliases.filter(domain=domain):
            lines.append(u'{alias.account_name}: {person.email}'.format(
                alias=alias,
                person=person,
            ))

        lines.append('')

    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=UTF-8')


@handle_api_errors
@api_login_required
def access_admin_smtppasswd_api(request, smtp_server_hostname):
    smtp_server = get_object_or_404(SMTPServer, hostname=smtp_server_hostname)

    lines = []

    for smtp_password in smtp_server.smtp_passwords.all():
        lines.append('{username}:{password_hash}:{full_name}'.format(
            username=smtp_password.person.user.username,
            password_hash=smtp_password.password_hash,
            full_name=smtp_password.person.full_name,
        ))

    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=UTF-8')


@access_admin_required
def access_admin_aliases_view(request, vars, organization):
    aliases = EmailAlias.objects.filter(domain__organization=organization).order_by('person')

    vars.update(
        aliases=aliases,
    )

    return render(request, 'access_admin_aliases_view.jade', vars)


def access_admin_menu_items(request, organization):
    aliases_url = url('access_admin_aliases_view', organization.slug)
    aliases_active = request.path == aliases_url
    aliases_text = u'Sähköpostialiakset'

    return [(aliases_active, aliases_url, aliases_text)]