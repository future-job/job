from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.main_page, name='main_page'),
    url(r'^detail', views.detail_page, name='detail_page'),
    url(r'^list', views.list_page, name='list_page'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.post_edit, name='post_edit'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)