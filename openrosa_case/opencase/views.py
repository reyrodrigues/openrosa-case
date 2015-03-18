from __future__ import absolute_import, unicode_literals, division, print_function

import StringIO
import os

from django.conf import settings

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import requests
import xmltodict
import tinydb

from . import builder
import lxml.etree as ET
from . import models
from . import odk_client
from . import decorators
from . import utils


LOCALES = (
    ('en', 'English'),
    ('default', 'Default')
)


def profile(request, application_slug):
    application = get_object_or_404(models.Application, slug=application_slug)
    current_locale = 'en'
    path = request.build_absolute_uri('/cases/%s' % application_slug)

    element = builder.build_profile(application, path, current_locale)
    return HttpResponse(ET.tostring(element))


def suite(request, application_slug):
    application = get_object_or_404(models.Application, slug=application_slug)
    element = builder.build_suite(application)
    return HttpResponse(ET.tostring(element))


def app_strings(request, application_slug, locale):
    application = get_object_or_404(models.Application, slug=application_slug)

    return HttpResponse(builder.build_app_strings(application, locale))


def form_by_index(request, application_slug, module_index, form_index):
    application = get_object_or_404(models.Application, slug=application_slug)

    module = application.modules.order_by('index')[int(module_index)]
    form = module.forms.order_by('index')[int(form_index)]

    element = odk_client.transform_form(form.form_url,
                                        version=str(application.version),
                                        form=form)
    return HttpResponse(ET.tostring(element))


@decorators.basic_http_auth
def keys(request, application_slug):
    application = get_object_or_404(models.Application, slug=application_slug)

    element = builder.build_keys(application)
    return HttpResponse(ET.tostring(element))


def restore(request, application_slug):
    application = get_object_or_404(models.Application, slug=application_slug)

    db_dir = os.path.join(settings.BASE_DIR, 'dbs/{}.json'.format(application.slug))

    db = tinydb.TinyDB(db_dir)

    element = builder.build_restore(application, [xmltodict.unparse(c) for c in db.all()])

    return HttpResponse(ET.tostring(element))
    # return HttpResponse(response)


@csrf_exempt
def submit(request, application_slug):
    application = get_object_or_404(models.Application, slug=application_slug)
    files = request.FILES.iteritems()
    by_urls = {}
    for k, f in files:
        content = f.read()
        e = ET.fromstring(bytes(content.encode('utf-8')))

        nsmap = dict(
            f=e.nsmap[None],
            x="http://openrosa.org/jr/xforms",
            irc="http://rescue.org/xforms",
            c="http://commcarehq.org/case/transaction/v2"
        )

        data = e.xpath('/f:data', namespaces=nsmap)
        if data:
            data = data.pop()
            case_information = e.xpath('/f:data/c:case', namespaces=nsmap)
            if case_information:
                case_information = case_information.pop()
                parsed = xmltodict.parse(ET.tostring(case_information),
                                         process_namespaces=True,
                                         namespaces={"http://commcarehq.org/case/transaction/v2": None})

                db_dir = os.path.join(settings.BASE_DIR, 'dbs/{}.json'.format(application.slug))

                db = tinydb.TinyDB(db_dir)
                results = db.search(tinydb.where('case').has('@case_id') == parsed['case']['@case_id'])

                if results:
                    case = utils.dict_merge(results[0], parsed)
                    db.update(case, tinydb.where('case').has('@case_id') == parsed['case']['@case_id'])
                else:
                    db.insert(parsed)

                data.remove(case_information)
            if None in e.nsmap and 'http://openrosa.org/formdesigner/' in nsmap['f']:
                form_namespace = nsmap['f'].split('/')[-1]
                form = models.Form.objects.get(namespace=form_namespace)
                destination = form.submission_url

                if not destination in by_urls:
                    by_urls[destination] = {}

                by_urls[destination][k] = StringIO.StringIO(ET.tostring(data))
        else:
            ET.dump(e)

    for url, forms in by_urls.iteritems():
        requests.post(url, files=forms, auth=("reyrodrigues", "P@ssw0rd"))

    return HttpResponse()