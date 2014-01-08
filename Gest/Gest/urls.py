# -*- encoding: utf-8 -*-
import os , sys 
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', login, {'template_name': 'log-in.html', }, name="login"),
    url(r'^MenuAdmin$', views.MenuAdmin, name='MenuAdmin'),
    url(r'^MenuServicio$', views.MenuServicio, name='MenuServicio'),
    url(r'^MenuTaller$', views.MenuTaller, name='MenuTaller'),
    url(r'^MenuMecanico$', views.MenuMecanico, name='MenuMecanico'),
    url(r'^MenuBodega$', views.MenuBodega, name='MenuBodega'),
    url(r'^home$', views.home, name='home'),
    url(r'^informes$', views.informes, name='informes'),
    url(r'^construccion$', views.construccion, name='construccion'),
    url(r'^ingresaUsuario$', views.ingresausuario, name='ingresausuario'),
    url(r'^eliminausuario$', views.eliminausuario, name='eliminausuario'),
    url(r'^ingresaventa$', views.ingresaventa, name='ingresaventa'),
    url(r'^ingresamaterial$', views.ingresamaterial, name='ingresamaterial'),
    url(r'^regivehiculo$', views.regivehiculo, name='regivehiculo'),
    url(r'^regiproveedor$', views.regiproveedor, name='regiproveedor'),
    url(r'^modificaUsuario$', views.modificausuario, name='modificausuario'),
    url(r'^VehiculoList$', views.vehiculo_list, name='vehiculo_list'),
    url(r'^ventaList$', views.venta_list, name='venta_list'),
    url(r'^clienteList$', views.cliente_list, name='cliente_list'),
    url(r'^verclientes$', views.verclientes, name='verclientes'),
    url(r'^vermaterial$', views.vermaterial, name='vermaterial'),
    url(r'^buscarcliente$', views.buscarcliente, name='buscarcliente'),
    url(r'^buscaot$', views.buscaot, name='buscaot'),
    url(r'^buscaotMecanico$', views.buscaotMecanico, name='buscaotMecanico'),
    url(r'^buscarvehiculo$', views.buscarvehiculo, name='buscarvehiculo'),
    url(r'^buscarprov$', views.buscarprov, name='buscarprov'),
    url(r'^anulaot$', views.anulaot, name='anulaot'),
    url(r'^ingresaorden$', views.ingresaorden, name='ingresaorden'),
    url(r'^logout$', logout, {'template_name': 'volver.html', }, name="logout"),
    url(r'^main$', views.main, name='main'),
    url(r'^regicliente$', views.regicliente, name='regicliente'),
    (r'%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), 
    'django.views.static.serve',
    {'document_root' : settings.STATIC_ROOT }),
   
   
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
