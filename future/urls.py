# -*- coding: utf-8 -*-

"""future URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
# from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static
from future import settings


urlpatterns = [
    url(r'', include('ft_admin.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static('/future/upload/', document_root=settings.MEDIA_ROOT)

# ^ 문자열이 시작할 떄
# $ 문자열이 끝날 때
# \d 숫자
# + 바로 앞에 나오는 항목이 계속 나올 때
# () 패턴의 부분을 저장할 때