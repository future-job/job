# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from .models import Category, Content, ContentDetail, ContentCategory
import re
# Create your views here.

def main_page(request):
    return render(request, 'blog/index.html')

def list_page(request):
    # interviews = Content.objects.order_by('id')
    # print interviews.values()
    # context = {'interviews': interviews}
    # return render(request, 'blog/list.html', context)
    contents = Content.objects.filter(is_view=True).order_by('-id')
    contents_list = []

    for i, value in enumerate(contents):
        # print len(ContentCategory.objects.filter(content_id=value.id))
        if len(ContentCategory.objects.filter(content_id=value.id)):
            category_id = ContentCategory.objects.get(content_id=value.id).category_id
            tag = Category.objects.get(id=category_id).name
        else:
            tag = ''
        # print ContentDetail.objects.get(content_id=value.id).summary_desc
        contents_list.append({
            'title': value.title,
            'index': i, 'id': value.id,
            'summary_desc': re.sub(r"\r\n", "<br/>", ContentDetail.objects.get(content_id=value.id).summary_desc.replace("'", '`')),
            'thumbnail': str(ContentDetail.objects.get(content_id=value.id).image_01),
            'tag': tag
        })

    result = dict()
    result['contents_list'] = contents_list
    # print contents_list

    return render(request, 'blog/list.html', result)

def detail_page(request):
    content_id = int(request.GET.get('content_no', -1))
    detail = ContentDetail.objects.get(content_id=content_id)
    content = Content.objects.get(id=content_id)
    meta_info = dict()
    meta_info['title'] = content.title
    meta_info['thumbnail'] = str(detail.image_01)
    meta_info['description'] = detail.summary_desc
    meta_info['goodjob'] = content.good_job
    # print "metaInfo : ", meta_info['description']
    return render(request, 'blog/detail.html', meta_info)

def custom_admin(request):
    return render(request, 'blog/admin.html')

def custom_admin_detail(request):
    # def dispatch(self, *args, **kwargs):
    #     return super(BoardSearchView, self).dispatch(*args, **kwargs)
    #
    # contend_id = kwargs['contend_id']
    # data = dict()
    # data["content_id"] = contend_id
    return render(request, 'blog/admin_detail.html')