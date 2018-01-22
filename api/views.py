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
# from libs.submodels.member import Member, MemberGrade, MemberDetail, MemberTerms, TermForm, SessionStore,\
#     MemberSession, ShoppingBasket, NonMember, SendMsgHistory, StockNotification, BankCode, MemberGradeHistory, LoginUniqueID, VerifyPossessionOfPhone
# from libs.submodels.member_point import SerialCoupon, Mileage, MileageUsageHistory, Deposit, Coupon
# from libs.submodels.order import Order, OrderItem, PaymentInfo, ShippingAddress, PaidCompany, OrderItemRecall, PayMethod, OrderAction, StockArrivalRemind
# from libs.submodels.promotion import Promotion
# from libs.submodels.product import Product, ProductOption, Category, ProductCategory, ProductDetail, Stock, \
#     RelationProduct, TogetherBuyItem, SetProductConstruct, ProductPrice
# from libs.submodels.shop import ShopMainPageSlider, ShopMainPageBanner
# from libs.submodels.board import QABoard, QAProductBoard, ReviewBoard, NoticeBoard, Comment
# from libs.payment_core import PaymentManager, IamportManager
from django.db.models import Q, Sum, F
from django.db.models import ObjectDoesNotExist

from django.forms.models import model_to_dict
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.core import serializers

# from Crypto import Random
# from Crypto.Cipher import AES

# from libs.core import ShopErrorTable
# from libs.core import Calc, OrderManager, ProductCacheManager, ProductManager, MemberManager, CommonManager, \
#     OrderAdminManager, DeliveryAddCost
# from libs.core import DeliveryManager, PaymentInfoManager, OrderInfos
# from libs.core import to_dict, sendEventMailJoin, send_eventmail_verification
# from libs.order_core import complete_order, cancel_order_items, exchange_order_items, complete_bank_transfer_payment, get_promotion_gift_info_of_order, update_account_num
# from libs.core import Media, AESCipher
# from libs.biztalk_core import BiztalkManager
# from libs.member_core import InactiveMemberManager

# from libs.tasks import send_email, send_order_contents_email, send_sms, task_send_email
# from django_user_agents.utils import get_user_agent
from copy import deepcopy
import uuid

from django.shortcuts import render

# Create your views here.

DEBUG = getattr(settings, 'DEBUG')
CSRF_WHITELIST = getattr(settings, 'CSRF_WHITELIST')
TEST_MEMBER_ID = 976
EMPTY = ''
BASE_URL = 'danoshop.net'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SHOP_MEMBER_SESSION_KEY = getattr(settings, 'SHOP_MEMBER_SESSION_KEY', '_shop_member_session')

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

        all_contents = Content.objects.all()
        # print '-----------------all_contents-----------------'
        # print all_contents

        contents = Content.objects.filter(is_view=True).order_by('id')
        contents_list = []

        # print ('contents : %s', contents)
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

class ContentDetailView(View):
    def get(self, request, **kwargs):
        result = dict()

        content_id = int(request.GET.get('content_no', -1))
        detail = ContentDetail.objects.get(content_id=content_id)
        contents = Content.objects.filter(is_view=True).order_by('id')
        if len(ContentCategory.objects.filter(content_id=content_id)):
            category = ContentCategory.objects.get(content_id=content_id).category_id
            tag_name = Category.objects.get(id=category).name
        else:
            tag_name = ''

        contents_list = []
        for i, value in enumerate(contents):
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
                data = dict()
                data['id'] = content.id
                data['title'] = content.title
                data['reg_time'] = str(content.reg_time)
                data['summary_desc'] = detail.summary_desc
                data['detail_desc'] = detail.detail_desc
                data['thumbnail'] = str(detail.image_01)
                data['contents'] = contents_list
                data['tag'] = tag_name
                result['error'] = 0
                result['data'] = data

        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='application/json')

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

        # if check_email_exist(email):
        #     result = dict(error=602, msg=u"이미 존재하는 E-mail입니다.", data=dict())
        #     return HttpResponse(json.dumps(result, ensure_ascii=False))
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