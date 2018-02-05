# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.core import serializers

import time
import re
import os
import hashlib
import base64
import ast
import sys
from datetime import timedelta, datetime, date
from random import randint
from django.utils import timezone
from django.conf import settings
from django.middleware import csrf
from django.http import QueryDict

from django.shortcuts import render
from ft_admin.models import Category, Content, ContentDetail, ContentCategory, Member
from api.core import sendDetailEmail

from django.views import View
from django.http import HttpResponse


DEBUG = getattr(settings, 'DEBUG')
CSRF_WHITELIST = getattr(settings, 'CSRF_WHITELIST')
TEST_MEMBER_ID = 976
EMPTY = ''
BASE_URL = 'danoshop.net'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SHOP_MEMBER_SESSION_KEY = getattr(settings, 'SHOP_MEMBER_SESSION_KEY', '_shop_member_session')

def save_board_file(fname, upload_f):

    base_path = settings.MEDIA_ROOT
    print 'base_path : ', base_path
    now = datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    if os.path.exists(base_path+ year) is False:
        os.mkdir(base_path+year, 0777)

    if os.path.exists(base_path + '%s/%s'%(year, month) ) is False:
        os.mkdir(base_path+"%s/%s"%(year, month), 0777)

    if os.path.exists(base_path + '%s/%s/%s'%(year, month, day) ) is False:
        os.mkdir(base_path+"%s/%s/%s"%(year, month, day), 0777)

    path = base_path + '%s/%s/%s/%s'%(year, month, day, fname)
    print path
    try:
        print 'image save try..'
        with open(path, 'wb+') as f:
            for chunk in upload_f.chunks():
                f.write(chunk)
    except:
        print 'image save failed..'
        raise Exception(fname+'FILE UPLOAD FAIL.')

    return '%s/%s/%s/%s'%(year, month, day, fname)

class ServerStatusView(View):
    def get(self, request, **kwargs):
        result = dict()
        # print 'CSRF get host: %s' % request.get_host()

        referer = None
        # print request.META
        # print request.is_secure()

        res = HttpResponse(json.dumps(result, ensure_ascii=False))

        if 'HTTP_REFERER' in request.META:
            referer = request.META['HTTP_REFERER']
        if not referer:
            # print 'no-referer set ip'
            referer = request.META['REMOTE_ADDR']

        # http://m.shop.dano.me/member/login
        # print 'hans_tmp_log :' + referer
        has_access_host = re.search('^http[s]?:[/]{2}(.*?)[/]', referer)
        if has_access_host:
            referer = has_access_host.group(1)
        print 'hans_tmp_log : {}\n{}'.format(request.META, request.COOKIES)
        if referer and BASE_URL == referer:
            print 'request is SAME dormain, SET Token'
            csrf.get_token(request)
        elif referer:
            for white in CSRF_WHITELIST:
                if white == referer:
                    print 'request is allowed Cross domain, SET Token', white, referer
                    token = csrf.get_token(request)
                    res['X-CSRFToken'] = token
                    res['Access-Control-Expose-Headers'] = 'X-CSRFToken'
                    # 해당 Expose 처리를 안하면, 추가한 헤더가 넘어가질 않음 (cross 도메인시)
                    break
        else:
            pass

        return res

class ContentListView(View):
    def get(self, request, **kwargs):
        result = dict()

        contents = Content.objects.filter(is_view=True).order_by('-id')
        contents_list = []

        for i, value in enumerate(contents):
            print len(ContentCategory.objects.filter(content_id=value.id))
            if len(ContentCategory.objects.filter(content_id=value.id)):
                category_id = ContentCategory.objects.get(content_id=value.id).category_id
                tag = Category.objects.get(id=category_id).name
            else:
                tag = ''
            contents_list.append({
                'title': value.title,
                'index': i, 'id': value.id,
                'summary_desc': ContentDetail.objects.get(content_id=value.id).summary_desc.replace('\n', '<br/>'),
                'thumbnail': str(ContentDetail.objects.get(content_id=value.id).image_01),
                'tag': tag
            })
        print ('contents_list : %s', contents_list)

        # contents_temp = serializers.serialize('json', contents_list)

        result['contents'] = contents_list
        result['error'] = 0

        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='application/json')

class AdminContentListView(View):
    def get(self, request, **kwargs):
        result = dict()

        contents = Content.objects.all().order_by('-id')
        contents_list = []

        for i, value in enumerate(contents):
            print len(ContentCategory.objects.filter(content_id=value.id))
            if len(ContentCategory.objects.filter(content_id=value.id)):
                category_id = ContentCategory.objects.get(content_id=value.id).category_id
                tag = Category.objects.get(id=category_id).name
            else:
                tag = ''
            contents_list.append({
                'title': value.title,
                'index': i,
                'id': value.id,
                'tag': tag,
                'good_job': value.good_job,

            })
        print ('contents_list : %s', contents_list)

        # contents_temp = serializers.serialize('json', contents_list)

        result['contents'] = contents_list
        result['error'] = 0

        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='application/json')

class AdminContentDetailView(View):
    def dispatch(self, request, *args, **kwargs):

        if request.method == 'PUT':
            if hasattr(request, '_post'):
                del request._post
                del request._files
            try:
                request.method = "POST"
                request._load_post_and_files()
                request.method = "PUT"
            except AttributeError:
                print 'Attribute Error..???'
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = 'PUT'

            request.PUT = request.POST

        elif request.method == 'DELETE':
            if hasattr(request, '_post'):
                del request._post
                del request._files
            try:
                request.method = "POST"
                request._load_post_and_files()
                request.method = "DELETE"
            except AttributeError:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = 'DELETE'

            request.DELETE = request.POST

        return super(AdminContentDetailView, self).dispatch(request, *args, **kwargs)


        # return super(AdminContentDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        result = dict()
        category_list = []
        categories = Category.objects.values()
        # category_name = Category.objects.values_list(self, 'name')
        # print category_list

        for i, value in enumerate(categories):
            print value['name'], value['id']
            category_list.append({
                'id' : value['id'],
                'name' : value['name'],
            })

        content_id = int(request.GET.get('content_no', -1))
        if(content_id != -1):
            detail = ContentDetail.objects.get(content_id=content_id)
            if(ContentCategory.objects.filter(content_id=content_id)):
                category_value = ContentCategory.objects.get(content_id=content_id).category_id
            else :
                category_value = 1

            if content_id == -1:
                result['error'] = 601
                result['msg'] = u'조회할 상품 정보를 알 수 없습니다.'
            else:
                content = Content.objects.get(id=content_id)

                if content is None:
                    result['error'] = 602
                    result['msg'] = u'존재하지 않는 상품 정보입니다.'
                else:
                    data = dict()
                    data['id'] = content.id
                    data['title'] = content.title
                    data['reg_time'] = str(content.reg_time)
                    data['summary_desc'] = detail.summary_desc
                    data['detail_desc'] = detail.detail_desc
                    data['thumbnail'] = str(detail.image_01)
                    data['is_view'] = content.is_view
                    data['category'] = category_value
                    data['category_list'] = category_list
                    result['error'] = 0
                    result['data'] = data
        else :
            data = dict()
            data['category_list'] = category_list
            result['error'] = 0
            result['data'] = data

        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='application/json')

    def post(self, request, **kwargs):

        content = Content()
        detail = ContentDetail()
        content_category = ContentCategory()

        is_view = request.POST.get('is_view', '')
        if is_view is 'false':
            content.is_view = False
        else :
            content.is_view = True

        title = request.POST.get('title', '')
        if title is '':
            result = dict(error=601, msg=u"제목은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        content.title = title

        reg_time = request.POST.get('reg_time', '')
        if reg_time is '':
            result = dict(error=601, msg=u"등록시간은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        content.reg_time = reg_time

        category_no = request.POST.get('category', '')
        if category_no is '':
            result = dict(error=601, msg=u"카테고리는 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        category = Category.objects.get(id=category_no)
        content_category.category = category

        summary_desc = request.POST.get('summary_desc', '')
        if summary_desc is '':
            result = dict(error=601, msg=u"요약설명은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        detail.summary_desc = summary_desc

        detail_desc = request.POST.get('detail_desc', '')
        if detail_desc is '':
            result = dict(error=601, msg=u"상세설명은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        detail.detail_desc = detail_desc


        if int(len(request.FILES.keys())) == 0:
            result = dict(error=601, msg=u"썸네일은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        else:
            upload_f = request.FILES['thumbnail']
            file_name = "%s_%s.%s" % ('thumbnail', str(time.time()).replace('.', ''), str(upload_f).split('.')[-1])
            print file_name, upload_f
            try:
                url = save_board_file(file_name, upload_f)
                print "save_board_file : ", url
                thumbnail_url = url
            except:
                thumbnail_url = ''
                pass

        detail.image_01 = thumbnail_url
        try:
            content.save()
            detail.content = content
            detail.save()
            content_category.content = content
            content_category.save()
        except:
            result = dict(error=600, msg=u"개발팀에 문의해주세요", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))


        result = dict(error=0, msg=u"포스트가 등록되었습니다", data=dict())

        return HttpResponse(json.dumps(result, ensure_ascii=False))

    def put(self, request, **kwargs):
        content_id = request.POST.get('content_no', 0)

        content = Content.objects.get(id=content_id)
        detail = ContentDetail.objects.get(content_id=content_id)
        content_category = ContentCategory.objects.get(content_id=content_id)

        is_view = request.POST.get('is_view', 0)
        print is_view
        if str(is_view) == '0':
            print 'is_view is False'
            content.is_view = False
        else:
            print 'is_view is True'
            content.is_view = True

        title = request.POST.get('title', '')
        if title is '':
            result = dict(error=601, msg=u"제목은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        content.title = title

        reg_time = request.POST.get('reg_time', '')
        if reg_time is '':
            result = dict(error=601, msg=u"등록시간은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        content.reg_time = reg_time

        category_no = request.POST.get('category', '')
        if category_no is '':
            result = dict(error=601, msg=u"카테고리는 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        summary_desc = request.POST.get('summary_desc', '')
        if summary_desc is '':
            result = dict(error=601, msg=u"요약설명은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        detail.summary_desc = summary_desc

        detail_desc = request.POST.get('detail_desc', '')
        if detail_desc is '':
            result = dict(error=601, msg=u"상세설명은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        detail.detail_desc = detail_desc

        print request.FILES.keys() ,len(request.FILES.keys()), int(len(request.FILES.keys()))
        if len(request.FILES.keys()) is not 0:
            upload_f = request.FILES['thumbnail']
            file_name = "%s_%s.%s" % ('thumbnail', str(time.time()).replace('.', ''), str(upload_f).split('.')[-1])
            print file_name, upload_f
            try:
                url = save_board_file(file_name, upload_f)
                print "save_board_file : ", url
                detail.image_01 = url
            except:
                pass


        try:
            content.save()
            # detail.content = content
            detail.save()
            content_category.category_id = category_no
            content_category.save()
        except:
            result = dict(error=600, msg=u"개발팀에 문의해주세요", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        result = dict(error=0, msg=u"포스트가 등록되었습니다", data=dict())

        return HttpResponse(json.dumps(result, ensure_ascii=False))

class ContentDetailView(View):
    def get(self, request, **kwargs):
        result = dict()
        content_id = int(request.GET.get('content_no', -1))
        detail = ContentDetail.objects.get(content_id=content_id)

        if len(ContentCategory.objects.filter(content_id=content_id)):
            category = ContentCategory.objects.get(content_id=content_id).category_id
            tag_name = Category.objects.get(id=category).name
        else:
            tag_name = ''


        print content_id

        if content_id == -1:
            result['error'] = 601
            result['msg'] = u'조회할 상품 정보를 알 수 없습니다.'
            # result['msg'] = self.get_error_msg(result['error'])
        else:
            content = Content.objects.get(id=content_id)
            # print content_info
            # print content.title, content.id, content.is_view, content.reg_time

            # print detail
            if content is None:
                result['error'] = 602
                result['msg'] = u'존재하지 않는 상품 정보입니다.'
            else:
                print 3
                data = dict()
                data['id'] = content.id
                data['title'] = content.title
                data['reg_time'] = str(content.reg_time)
                data['summary_desc'] = detail.summary_desc
                data['detail_desc'] = detail.detail_desc
                data['thumbnail'] = str(detail.image_01)
                data['tag'] = tag_name
                result['error'] = 0
                result['data'] = data

        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='application/json')

class ContentLikeView(View):
    def post(self, request, **kwargs):
        content_id = int(request.POST.get('content_no', -1))
        content = Content.objects.get(id=content_id)

        # print "content : ",
        content.good_job = content.good_job + 1

        try:
            content.save()
        except:
            result = dict(error=600, msg=u"개발팀에 문의해주세요", data=dict())
            return HttpResponse(result)

        data = dict()
        data["good_job"] = content.good_job

        result = dict(error=0, msg=u"Good Job을 해주셔서 감사합니다", data=data)


        return HttpResponse(json.dumps(result, ensure_ascii=False))

class MemberJoinView(View):
    def dispatch(self, *args, **kwargs):
        return super(MemberJoinView, self).dispatch(*args, **kwargs)

    # def get(self, request, **kwargs):
    #
    #     request_type = kwargs['request_type']
    #     if request_type == 'account':
    #         account = request.GET.get('account', '')
    #         print 'JOIN ACCOUNT', account
    #         if account is '':
    #             result = dict(error=602, msg=u"전달된 account 값이 없습니다", data=dict())
    #             return HttpResponse(json.dumps(result, ensure_ascii=False))
    #         is_account_exist = check_account_exist(account)
    #         if is_account_exist:
    #             result = dict(error=601, msg=u"이미 존재하는 계정입니다.", data=dict())
    #         else:
    #             result = dict(error=0, msg=u"사용 가능한 계정입니다.", data=dict())
    #
    #     elif request_type == 'phone':
    #         phone = request.GET.get('phone', '')
    #         print 'JOIN phone',phone
    #         if check_phone_validate(phone) is False:
    #             result = dict(error=601, msg=u"올바른 번호를 입력해주세요.", data=dict())
    #             print result['msg']
    #             return HttpResponse(json.dumps(result, ensure_ascii=False))
    #
    #         if Member.objects.filter(phone=phone).exists():
    #             result = dict(error=610, msg=u"이미 가입된 휴대폰 번호입니다.", data=dict())
    #             return HttpResponse(json.dumps(result, ensure_ascii=False))
    #
    #         result = dict(error=0, msg="", data=dict())
    #
    #     elif request_type == 'email':
    #         email = request.GET.get('email', '')
    #         print 'check email: %s' % email
    #         is_email_exist = check_email_exist(email)
    #         if is_email_exist:
    #             result = dict(error=601, msg=u"이미 존재하는 E-mail 입니다.", data=dict())
    #         else:
    #             result = dict(error=0, msg=u"사용 가능한 E-mail 입니다.", data=dict())
    #
    #     return HttpResponse(json.dumps(result, ensure_ascii=False))

    def post(self, request, **kwargs):

        # request_type = kwargs['request_type']
        # if request_type != 'apply':
        #     result = dict(error=401, msg=u"올바르지 않은 요청입니다.", data=dict())
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))

        member = Member()

        # name = request.POST.get('email', '')
        # if name is '':
        #     result = dict(error=601, msg=u"email 은 필수 입력값 입니다.", data=dict())
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))
        #
        # member.email = email

        age = request.POST.get('age', '')
        if age is '':
            result = dict(error=601, msg=u"나이는 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        member.age = age
        # is_account_exist = check_account_exist(account)
        # if is_account_exist:
        #     result = dict(error=602, msg=u"이미 존재하는 계정입니다.", data=dict())
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))
        # member.account = account

        email = request.POST.get('email', '')
        if email is '':
            result = dict(error=601, msg=u"이메일은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        def check_email_exist(email):
            return Member.objects.filter(email=email).exists()

        if check_email_exist(email):
            result = dict(error=602, msg=u"이미 존재하는 E-mail입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        member.email = email

        # join_channel = request.POST.get('join_channel', '')
        # member.join_channel = join_channel

        job = request.POST.get('job', '')
        if job is '':
            result = dict(error=601, msg=u"직업은 필수 입력값 입니다.", data=dict())
            return HttpResponse(json.dumps(result, ensure_ascii=False))

        # if check_phone_validate(phone) is False:
        #     result = dict(error=601, msg=u"올바른 번호를 입력해주세요.", data=dict())
        #     print result['msg']
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))
        #
        # if Member.objects.filter(phone=phone).exists():
        #     result = dict(error=610, msg=u"이미 가입된 휴대폰 번호입니다.", data=dict())
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))

        member.job = job

        print "member : ", member

        try:
            member.save()
        except:
            result = dict(error=600, msg=u"개발팀에 문의해주세요", data=dict())
            return HttpResponse(result)


        # member_detail = Member.objects.create(member=member)
        # print "member_detail : ", member_detail
        # member_detail.save()

        result = dict(error=0, msg=u"구독 신청이 되었습니다", data=dict())

        #회원가입 안내메일
        # sendEventMailJoin(member)

        return HttpResponse(json.dumps(result, ensure_ascii=False))

class SendEmailView(View):
    def post(self, request, **kwargs):
        content_id = int(request.POST.get('content_no', -1))
        member = Member.objects.values('email')
        member_list = []
        for i, value in enumerate(member):
            print i, value[u'email']
            member_list.append(value[u'email'])
            #     category_id = ContentCategory.objects.get(content_id=value.id).category_id
            #     tag = Category.objects.get(id=category_id).name
            # else:
            #     tag = ''
            # contents_list.append({
            #     'title': value.title,
            #     'index': i, 'id': value.id,
            #     'summary_desc': ContentDetail.objects.get(content_id=value.id).summary_desc.replace('\n', '<br/>'),
            #     'thumbnail': str(ContentDetail.objects.get(content_id=value.id).image_01),
            #     'tag': tag
            # })
        print "hello : ", member_list
        sendDetailEmail(member_list, content_id)


            # try:
            #     content.save()
            # except:
            #     result = dict(error=600, msg=u"개발팀에 문의해주세요", data=dict())
            #     return HttpResponse(result)

            # data = dict()
            # data["good_job"] = content.good_job

        result = dict(error=0, msg=u"이메일 발송 완료", data=dict())

        return HttpResponse(json.dumps(result, ensure_ascii=False))