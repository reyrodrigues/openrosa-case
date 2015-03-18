from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.http import HttpResponse
from django.contrib.auth import authenticate
from . import models
import base64
from django.contrib.auth.hashers import make_password


def basic_http_auth(f):
    def wrap(request, *args, **kwargs):
        if request.META.get('HTTP_AUTHORIZATION', False):
            authtype, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
            auth = base64.b64decode(auth)
            domain_user, password = auth.split(':')
            username, domain = domain_user.split('@')
            salted = ''

            application = models.Application.objects.filter(slug=domain)
            if application:
                application = application[0]

            user = application.users.filter(username=username)
            if user:
                user = user[0]
                salt = user.password.split('$')[1]
                salted = make_password(password, salt=salt, hasher='sha1')

            if application and user and salted == user.password:
                return f(request, *args, **kwargs)
            else:
                r = HttpResponse("Auth Required", status=401)
                r['WWW-Authenticate'] = 'Basic realm="basic"'
                return r
        r = HttpResponse("Auth Required", status=401)
        r['WWW-Authenticate'] = 'Basic realm="basic"'
        return r

    return wrap