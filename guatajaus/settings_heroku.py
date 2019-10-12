# -*- coding: utf-8 -*-

from .settings import *
import django_heroku

DEBUG = False
ALLOWED_HOSTS = ['guatajaus.herokuapp.com']

django_heroku.settings(locals())
