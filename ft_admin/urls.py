# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^start', views.main_page, name='main_page'),
    url(r'^detail', views.detail_page, name='detail_page'),
    url(r'^future/admin/member', views.custom_admin_member, name='admin_page'),
    url(r'^future/admin/detail', views.custom_admin_detail, name='admin_page'),
    url(r'^future/admin/main', views.custom_admin, name='admin_page'),
    url(r'^$', views.list_page, name='list_page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)