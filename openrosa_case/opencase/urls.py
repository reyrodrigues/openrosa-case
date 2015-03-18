from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import views

urls = (
    '',
    url(r'(?P<application_slug>[\d\-\w]+)/profile', views.profile),
    url(r'(?P<application_slug>[\d\-\w]+)/suite', views.suite),
    url(r'(?P<application_slug>[\d\-\w]+)/keys/', views.keys),
    url(r'(?P<application_slug>[\d\-\w]+)/restore/', views.restore),
    url(r'(?P<application_slug>[\d\-\w]+)/submit/', views.submit),
    url(r'(?P<application_slug>[\d\-\w]+)/modules-(?P<module_index>[\d]+)/forms-(?P<form_index>[\d]+).xml',
        views.form_by_index),
    url(r'(?P<application_slug>[\d\-\w]+)/(?P<locale>[\d\-\w]+)/app_strings.txt', views.app_strings)
)

urlpatterns = patterns(*urls)