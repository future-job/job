# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from .models import Category, Content
# Create your views here.

def main_page(request):
    return render(request, 'blog/index.html')

def list_page(request):
    # interviews = Content.objects.order_by('id')
    # print interviews.values()
    # context = {'interviews': interviews}
    # return render(request, 'blog/list.html', context)
    return render(request, 'blog/list.html')

def detail_page(request):
    return render(request, 'blog/detail.html')
