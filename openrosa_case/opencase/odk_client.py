from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
import requests
import os
from lxml import etree as ET
from lxml.builder import ElementMaker, E

ODK_BASE_URL = "https://ona.rescue.org/reyrodrigues"
ODK_AUTH = ('reyrodrigues', 'P@ssw0rd')

C = ElementMaker(namespace="http://commcarehq.org/case/transaction/v2",
                 nsmap={None: "http://commcarehq.org/case/transaction/v2"})

META = ElementMaker(namespace="http://openrosa.org/jr/xforms",
                    nsmap={'orx': "http://openrosa.org/jr/xforms", 'cc': "http://commcarehq.org/xforms"})

CC = ElementMaker(namespace="http://commcarehq.org/xforms", nsmap={'cc': "http://commcarehq.org/xforms"})


def list_forms():
    url = os.path.join(ODK_BASE_URL, 'formList')
    text = requests.get(url, auth=ODK_AUTH).text

    element = ET.XML(text)

    print(ET.tostring(element))


def get_form(url):
    text = requests.get(url, auth=ODK_AUTH).text

    element = ET.fromstring(bytes(text))

    return element
    # print(ET.tostring(element))


def build_case_xml(form, case_metadata, subcase_index=None):
    if not case_metadata or not case_metadata.case_module:
        module = form.module
    else:
        module = case_metadata.case_module

    if subcase_index is None:
        case_xpath = '/data/case'
    else:
        case_xpath = '/data/subcase_{}/case'.format(subcase_index)

    data_elements = []

    case = C.case({'case_id': "", 'date_modified': "", 'user_id': ""}, )
    if form.case_action == 'open':
        create = C.create(C.case_name(), C.owner_id(), C.case_type(module.case_type), )
        case.append(create)

        name_field = case_metadata.mapping.filter(direction=2, destination='case_name')[0]
        data_elements.append(E.bind({'calculate': name_field.origin, 'nodeset': case_xpath + '/create/case_name', }))
        # data_elements.append(E.bind({'calculate': '/data/meta/userID', 'nodeset': case_xpath + '/create/owner_id', }))
        data_elements.append(E.setvalue({
            'event': 'xforms-ready',
            'ref': case_xpath + '/create/owner_id',
            'value': 'instance(\'groups\')/groups/group/@id'
        }))

        data_elements.append(E.setvalue({'event': 'xforms-ready', 'ref': case_xpath + '/@case_id', 'value': 'uuid()'}))
    elif form.case_action == 'update':
        data_elements.append(E.bind({'calculate': "instance('commcaresession')/session/data/case_id",
                                     'nodeset': case_xpath + '/@case_id', }))

    mapped = case_metadata.mapping.filter(direction=2)

    if form.case_action == 'open':
        mapped = mapped.exclude(destination='case_name')

    if mapped:
        update = C.update()
        for m in mapped:
            update.append(ET.Element(m.destination))
            data_elements.append(E.bind({'calculate': m.origin, 'nodeset': case_xpath + '/update/' + m.destination, }))
        case.append(update)

    for m in case_metadata.mapping.filter(direction=1):
        data_elements.append(E.setvalue({
            'event': 'xforms-ready',
            'ref': m.destination,
            'value': "instance('casedb')/casedb/case[@case_id=instance('commcaresession')" +
                     "/session/data/case_id]/{}".format(m.origin)
        }))

    data_elements.append(E.bind({
        'calculate': '/data/meta/timeEnd',
        'nodeset': case_xpath + '/@date_modified',
        'type': 'xsd:dateTime',
    }))
    data_elements.append(E.bind({'calculate': '/data/meta/userID', 'nodeset': case_xpath + '/@user_id', }))

    if subcase_index is not None and form.cases.filter(case_module__isnull=True):
        parent_case_type = form.module.case_type
        case.append(C.index(C.parent({"case_type": parent_case_type})))
        data_elements.append(E.bind({'calculate': '/data/case/@case_id', 'nodeset': case_xpath + '/index/parent', }))

    return case, data_elements


def transform_form(url, version="1", form=None):
    """
    This function takes in an xform from Formhub and transforms it into something that the commcare app would accept
    :param url:
    :return:
    """
    text = requests.get(url, auth=ODK_AUTH).text

    # Load XML as bytes because lxml won't take in unicode
    element = ET.fromstring(bytes(text.encode('utf-8')))

    # Namespaces are the sole reason people don't use XML anymore
    nsmap = dict([(k, v) for k, v in element.nsmap.iteritems() if k])
    nsmap['xf'] = "http://www.w3.org/2002/xforms"

    title = element.xpath('//h:title', namespaces=nsmap).pop().text

    # Add default namespace and new attributes to the data element
    data = element.xpath('//h:html/h:head/xf:model/xf:instance/xf:data', namespaces=nsmap).pop()
    old_meta = element.xpath('//h:html/h:head/xf:model/xf:instance/xf:data/xf:meta', namespaces=nsmap).pop()

    instance = data.getparent()

    data_ns = data.nsmap
    data_ns[None] = "http://openrosa.org/formdesigner/" + form.namespace
    data.remove(old_meta)

    new_data = ET.Element(data.tag, nsmap=data_ns)
    new_data[:] = data[:]
    new_data.attrib.update(data.attrib)
    new_data.attrib['name'] = title
    new_data.attrib['uiVersion'] = "1"
    new_data.attrib['version'] = version

    instance.replace(data, new_data)
    model = instance.getparent()

    # Remove formhub UUID string
    bind = element.xpath('//xf:bind[@nodeset="/data/meta/instanceID"]', namespaces=nsmap)
    for b in bind:
        b.getparent().remove(b)

    # Case Element

    # New meta tag and CommCare

    meta = META.meta(
        META.deviceID(),
        META.timeStart(),
        META.timeEnd(),
        META.username(),
        META.userID(),
        META.instanceID(),
        CC.appVersion(),
    )

    new_data.append(meta)

    # Commcare Instances
    model.append(E.instance({'id': 'commcaresession', 'src': 'jr://instance/session'}))
    model.append(E.instance({'id': 'groups', 'src': 'jr://fixture/user-groups'}))
    model.append(E.instance({'id': 'casedb', 'src': 'jr://instance/casedb'}))

    # the example here is a Create Case, but this could also be an update or delete
    header_case_metadata = form.cases.filter(case_module__isnull=True)
    if form.case_action in ('open', 'update') and header_case_metadata:
        case, data_elements = build_case_xml(form, header_case_metadata[0])
        new_data.append(case)

        for e in data_elements:
            model.append(e)

    subcases = form.cases.filter(case_module__isnull=False)
    for index, subcase in enumerate(subcases):
        subcase_element = ET.Element('subcase_' + str(index))
        case, data_elements = build_case_xml(form, subcase, index)

        subcase_element.append(case)
        new_data.append(subcase_element)

        for e in data_elements:
            model.append(e)
    # end new case def

    # New Meta
    model.append(E.bind({'type': 'xsd:dateTime', 'nodeset': '/data/meta/timeStart', }))
    model.append(E.bind({'type': 'xsd:dateTime', 'nodeset': '/data/meta/timeEnd', }))

    model.append(E.setvalue({
        'event': 'xforms-ready',
        'ref': '/data/meta/deviceID',
        'value': "instance('commcaresession')/session/context/deviceid"
    }))
    model.append(E.setvalue({
        'event': 'xforms-ready',
        'ref': '/data/meta/username',
        'value': "instance('commcaresession')/session/context/username"
    }))
    model.append(E.setvalue({
        'event': 'xforms-ready',
        'ref': '/data/meta/userID',
        'value': "instance('commcaresession')/session/context/userid"
    }))
    model.append(E.setvalue({
        'event': 'xforms-ready',
        'ref': '/data/meta/appVersion',
        'value': "instance('commcaresession')/session/context/appversion"
    }))

    model.append(E.setvalue({'event': 'xforms-ready', 'ref': '/data/meta/instanceID', 'value': 'uuid()'}))
    model.append(E.setvalue({'event': 'xforms-ready', 'ref': '/data/meta/timeStart', 'value': 'now()'}))
    model.append(E.setvalue({'event': 'xforms-revalidate', 'ref': '/data/meta/timeEnd', 'value': 'now()'}))
    # End New Meta

    return element
