from __future__ import absolute_import, unicode_literals, division, print_function

import datetime
import uuid

from django.template.loader import get_template
from django.template import Context
from lxml.builder import E, ElementMaker

import lxml.etree as ET


__author__ = 'reyrodrigues'

LOCALES = (
    ('en', 'English'),
    ('default', 'Default')
)

DISPLAY_TYPES = ('case_short', 'case_long')

ORR = ElementMaker(namespace="http://openrosa.org/http/response",
                   nsmap={None: "http://openrosa.org/http/response"})
S = ElementMaker(namespace="http://commcarehq.org/sync",
                 nsmap={None: "http://commcarehq.org/sync"})
R = ElementMaker(namespace="http://openrosa.org/user/registration",
                 nsmap={None: "http://openrosa.org/user/registration"})
ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def _json_format_datetime(time):
    return time.strftime(ISO_FORMAT)

def _json_format_date(time):
    return time.strftime('%Y-%m-%d')


def build_app_strings(application, locale):
    # TODO: Localize me

    template = get_template('opencase/app_strings.txt')
    strings = []
    modules = application.modules.order_by('index')

    strings.append("homescreen.title={}".format(application.name))
    strings.append("app.display.name={}".format(application.name))

    for m_i, m in enumerate(modules):
        # Module Strings
        for display_type in DISPLAY_TYPES:
            strings.append('m{}.{}.title={}'.format(m_i, display_type, m.case_label))
            for i, t in enumerate(m.case_list_items.filter(type=display_type), start=1):
                strings.append("m{}.{}.{}_{}.header={}".format(m_i,
                                                               display_type,
                                                               t.property,
                                                               i,
                                                               (t.label or t.property)))

        strings.append("case_list.m{}={}".format(m_i, m.case_menu_item_label))
        strings.append("modules.m{}={}".format(m_i, m.name))

        # Forms Strings
        for f_i, f in enumerate(m.forms.order_by('index')):
            strings.append("forms.m{}f{}={}".format(m_i, f_i, f.name))

    context = Context({'strings': sorted(strings)})
    return template.render(context)


def build_suite(application):
    # TODO: Document the crap out of this

    template = get_template('opencase/suite.xml')
    modules = application.modules.order_by('index')

    suite = {
        'version': application.version,
        'descriptor': 'Suite File',
        'xforms': [],
        'entries': [],
        'details': [],
        'menus': [],
        'locales': LOCALES,
    }

    # Building XForms
    for m_i, m in enumerate(modules):
        for f_i, f in enumerate(m.forms.order_by('index')):
            suite['xforms'].append({
                'id': f.namespace,
                'descriptor': f.namespace,
                'relative_url': "./modules-{}/forms-{}.xml".format(m_i, f_i)
            })

    # Buiding Details
    for m_i, m in enumerate(modules):
        for display_type in DISPLAY_TYPES:
            suite['details'].append({
                'id': 'm{}_{}'.format(m_i, display_type),
                'locale_title_text': 'm{}.{}.title'.format(m_i, display_type),
                'fields': [
                    {
                        'locale_header_text': "m{}.{}.{}_{}.header".format(m_i, display_type, t.property, i),
                        'name': t.property
                    }
                    for i, t in enumerate(m.case_list_items.filter(type=display_type), start=1)
                ]
            })

    # Building Entries
    for m_i, m in enumerate(modules):
        for f_i, f in enumerate(m.forms.order_by('index')):
            entry = {
                "id": "m{}-f{}".format(m_i, f_i),
                "locale_text": "forms.m{}f{}".format(m_i, f_i),
                "namespace": f.namespace,
                "instances": [],
                "session_data": [],
            }

            if f.case_action in ['update']:
                entry['instances'].append({'id': 'casedb', 'src': 'jr://instance/casedb'})
                entry['session_data'].append({
                    "id": "case_id",
                    "nodeset": "instance('casedb')/casedb/case[@case_type='{}'][@status='open']".format(m.case_type),
                    "value": "./@case_id",
                    "select": "m{}_case_short".format(m_i),
                    "confirm": "m{}_case_long".format(m_i)
                })
            elif f.case_action in ['open']:
                entry['instances'].append({'id': 'groups', 'src': 'jr://fixture/user-groups'})

            suite['entries'].append(entry)

        if m.case_menu_item:
            entry = {
                "id": "m{}-case-list".format(m_i),
                "locale_text": "case_list.m{}".format(m_i),
                "instances": [],
                "session_data": [],
            }
            entry['instances'].append({'id': 'casedb', 'src': 'jr://instance/casedb'})
            entry['session_data'].append({
                "id": "case_id",
                "nodeset": "instance('casedb')/casedb/case[@case_type='{}'][@status='open']".format(m.case_type),
                "value": "./@case_id",
                "select": "m{}_case_short".format(m_i),
                "confirm": "m{}_case_long".format(m_i)
            })
            suite['entries'].append(entry)

    for m_i, m in enumerate(modules):
        if m.forms.count():
            menu = {
                'id': "m{}".format(m_i),
                "locale_text": "modules.m{}".format(m_i),
                'items': []
            }
            for f_i, f in enumerate(m.forms.order_by('index')):
                menu['items'].append({"id": "m{}-f{}".format(m_i, f_i), })
            if m.case_menu_item:
                menu['items'].append({"id": "m{}-case-list".format(m_i), })

            suite['menus'].append(menu)

    context = Context({'suite': suite})
    return ET.XML(bytes(template.render(context).encode('utf-8')))


def build_profile(application, path, current_locale):
    # TODO: Document the crap out of this
    profile_attributes = dict(version=str(application.version),
                              update=path + "/profile?latest=true",
                              requiredMajor="2",
                              requiredMinor="9",
                              descriptor="Profile File")

    profile_properties = {
        "ota-restore-url": path + "/restore/",
        "ota-restore-url-testing": path + "/restore/",
        "PostURL": path + "/submit/",
        "PostTestURL": path + "/submit/",
        "key_server": path + "/keys/",
        "cc_user_domain": application.slug,
        "cur_locale": current_locale,

        "BackupMode": "file_mode",
        "backup-url": "file:///E:/CommCare.Backup",
        "restore-url": "file:///E:/CommCare.Backup",
        "jr_openrosa_api": "1.0",
        "cc-days-form-retain": "1",
        "cc-show-saved": "yes",
        "unsent-time-limit": "1",
        "cc-autosync-freq": "freq-daily",
        "restore-tolerance": "loose",
        "cc-user-mode": "cc-u-normal",
        "cc-autoup-freq": "freq-never",
        "purge-freq": "0",
        "server-tether": "sync",
        "user_reg_server": "required",
        "extra_key_action": "audio",
        "log_prop_daily": "log_never",
        "ViewStyle": "v_chatterbox",
        "cc-resize-images": "none",
        "cc-entry-mode": "cc-entry-quick",
        "cc-send-procedure": "cc-send-http",
        "cc-login-images": "No",
        "log_prop_weekly": "log_short",
        "cc-show-incomplete": "yes",
        "cc-send-unsent": "cc-su-auto",
        "loose_media": "no",
        "password_format": "n",
        "unsent-number-limit": "10",
        "cc-content-valid": "yes",
        "logenabled": "Enabled",
    }

    element = E.profile(profile_attributes)

    for key in sorted(profile_properties.keys()):
        element.append(E.property(dict(key=key, value=profile_properties[key])))

    features = E.features(
        E.checkoff(dict(active="true")),
        E.reminders(dict(active="false"), E.time("0")),
        E.package(dict(active="false")),
        E.users(dict(active="true")),
    )

    element.append(features)

    suite_element = E.suite(
        E.resource(
            dict(id="suite", version=str(application.version)),
            E.location(dict(authority="local"), "./suite"),
            E.location(dict(authority="remote"), "./suite")
        )
    )

    element.append(suite_element)

    return element


def build_keys(application):
    valid_keys = application.keys.filter(expires__gt=datetime.datetime.now())

    if not valid_keys:
        key = application.keys.create()
        key.application = application
        key.save()
    else:
        key = valid_keys[0]
        key.expires = datetime.datetime.now() + datetime.timedelta(days=30)
        key.save()

    response = ORR.OpenRosaResponse(
        ORR.message({'nature': 'submit_success'}, "Here are your keys!"),
        ORR.auth_keys(
            {'domain': application.slug, 'issued': _json_format_datetime(key.valid)},
            ORR.key_record(
                {'valid': _json_format_datetime(key.valid),
                 'expires': _json_format_datetime(key.expires)},
                ORR.uuid(key.uuid),
                ORR.key({'type': 'AES256'}, key.key)
            )
        )
    )
    return response


def build_restore(application, cases):
    count = len(application.users.all()) + len(application.groups.all()) + len(cases)
    cases = [ET.XML(bytes(c.encode('utf-8'))) for c in cases]
    response = ORR.OpenRosaResponse(
        {"items": str(count)},
        ORR.message({'nature': 'ota_restore_success'}, "I'm not important!"),
        S.Sync(S.restore_id(str(uuid.uuid4()))),
    )

    for user in application.users.all():
        response.append(R.Registration(
            R.username(user.username),
            R.password(user.password),
            R.uuid(user.uuid),
            R.date(_json_format_date(user.created_on))
        ))
        response.append(ORR.fixture(
            {'id': 'user-groups', 'user_id': user.uuid},
            ORR.groups(
                ORR.group(
                    {'id': user.group.uuid},
                    ORR.name(user.group.name)
                )
            )
        ))

    for case in cases:
        case.attrib['xmlns'] = "http://commcarehq.org/case/transaction/v2"
        response.append(case)

    return response