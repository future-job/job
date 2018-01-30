# -*- coding: utf-8 -*-
import os, urllib, json, base64, hashlib, xlwt, sys, re

from libs.submodels.promotion import Promotion
from libs.submodels.member_point import SerialCoupon, Deposit, Mileage, Coupon

from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection
from django.db.models import Q, Sum, F, Count

from django.forms.models import model_to_dict

from datetime import date, datetime, timedelta
from Crypto.Cipher import AES

from copy import deepcopy
import time
from operator import itemgetter

import redis_lock
import redis
from django.conf import settings
from ft_admin.libs.tasks import send_email

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
REDIS_SERVER_IP = getattr(settings, 'REDIS_SERVER_IP')

reload(sys)
sys.setdefaultencoding('utf-8')




def sendDetailEmail(member):
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
    MAIL_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'libs/mail_templates/')

    title =
    msg = open(MAIL_TEMPLATES_DIR + 'detail.html', 'r').read()
    msg = msg.replace('{$title}', )
    msg = msg.replace('{tag}', )
    msg = msg.replace('{reg_date}', )
    msg = msg.replace('{descript_html}', )
    send_email(title, msg, [email, ])

def sendEventMailOrderComplete(order):
    if order.member:
        order_member = Member.objects.get(id=order.member.id)
        name = order_member.name
    elif order.non_member:
        order_member = NonMember.objects.get(id=order.non_member.id)
        name = order_member.name

    order_action = OrderAction.objects.get(order_num=order.num, type=0)
    total_product_price = order_action.total_product_price
    order_items = OrderItem.objects.filter(order_num=order.num).order_by('id')

    total_sale_price = order_action.promotion_discount + order_action.member_discount \
                       + order_action.coupon_discount
    shipping_cost = order_action.shipping_cost
    extra_shipping_cost = order_action.extra_shipping_cost
    mileage_use = order_action.mileage_use
    deposit_use = order_action.deposit_use

    main_pay_method = order.main_pay_method
    main_pay_method_str = ''

    sub_pay_method = False

    if main_pay_method == 0:
        main_pay_method_str = '신용카드'

    elif main_pay_method == 3:
        main_pay_method_str = '실시간계좌이체'

    elif main_pay_method == 4:
        main_pay_method_str = '무통장입금'

    elif main_pay_method == 6:
        main_pay_method_str = '휴대폰'

    elif main_pay_method == 7:
        main_pay_method_str = '가상계좌'

    else:
        sub_pay_method = True

    amount_to_pay = order_action.amount_to_pay

    shipping_address = order_items.first().address
    shipping_memo = shipping_address.shipping_memo

    if shipping_memo is None:
        shipping_memo = ''

    receiver_tel = ''

    zip_code = shipping_address.zip_code
    zip_address = shipping_address.zip_address
    address = shipping_address.address
    receiver_name = shipping_address.receiver_name
    receiver_tel = shipping_address.receiver_tel
    receiver_phone = shipping_address.receiver_phone

    product_html = ''
    temp_set_product = -1
    for order_item in order_items:
        if order_item.set_product_id:
            if temp_set_product == order_item.set_product.id:
                continue
            else:
                temp_set_product = order_item.set_product.id
                product_name = Product.objects.get(id=order_item.set_product.id).name
                product_img = ProductDetail.objects.get(product=order_item.set_product.id).image_02
                product_html += '<tr><th style="padding: 5px 0; text-align: left;"><img style="width: 80px;" src=\'https://danoshop.net/mall/upload/' + str(
                    product_img) + '\' /></th><!-- 옵션이 없을 경우, 해당 항목의 <div>태그 부분 삭제 --><td style="padding: 5px 10px; text-align: left;"><div style="padding-bottom: 3px; word-break: break-all;">' + product_name + '</div>'
                components = SetProductConstruct.get_components(order_item.set_product.id, order_item=order_item)
                temp_set_product_count = components.get(product_option=order_item.option).count
                temp_item_quantity = order_item.quantity / temp_set_product_count
                product_html += '<div style="font-size: 12px;">수량: ' + str(temp_item_quantity) + '개</div></td></tr>'

        else:
            product_name = Product.objects.get(id=order_item.product.id).name
            product_img = ProductDetail.objects.get(product=order_item.product.id).image_02
            product_html += '<tr><th style="padding: 5px 0; text-align: left;"><img style="width: 80px;" src=\'https://danoshop.net/mall/upload/' + str(
                product_img) + '\' /></th><!-- 옵션이 없을 경우, 해당 항목의 <div>태그 부분 삭제 --><td style="padding: 5px 10px; text-align: left;"><div style="padding-bottom: 3px; word-break: break-all;">' + product_name + '</div>'
            if ProductOption.objects.get(id=order_item.option.id).name != '기본':
                product_html += '<div style="font-size: 12px;">옵션: ' \
                                + ProductOption.objects.get(id=order_item.option.id).name + '</div>'

            product_html += '<div style="font-size: 12px;">수량: ' + str(order_item.quantity) + '개</div></td></tr>'

    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
    MAIL_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'libs/mail_templates/')

    html = open(MAIL_TEMPLATES_DIR + 'orderComplete.html', 'r').read()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    payer = ''
    paid_bank_name = ''
    paybank_account = ''
    paid_price = '';

    if sub_pay_method:
        soup.find('tr', id="paymethod-container").decompose()
        html = str(soup)

    if main_pay_method == PayMethod.BANK_TRANSFER:
        payment_info = PaymentInfo.objects.get(order_num=order.num, method=PayMethod.BANK_TRANSFER)
        paid_company = payment_info.paid_company
        paid_price = format(payment_info.price, ',')
        payer = payment_info.payer
        if paid_company.code == '020':
            paid_bank_name = '우리은행'
            paybank_account = '1005-502-842082'
        elif paid_company.code == '004':
            paid_bank_name = '국민은행'
            paybank_account = '822401-04-096330'

        html = html.replace('{$payer}', payer).replace('{$paid_bank_name}', paid_bank_name) \
            .replace('{$paybank_account}', paybank_account).replace('{$paid_price}', paid_price)

    else:
        for div_bankbook in soup.find_all("div", {'class': 'bankbook-container'}):
            div_bankbook.decompose()
            html = str(soup)

    title = u'다노샵에서 주문하신 내역이에요'

    html = html.replace('{$name}', name).replace('{$order_num}', order.num) \
        .replace('{$order_time}', str(order.reg_time)[:16])

    total_product_price = format(total_product_price, ',')
    total_sale_price = format(total_sale_price, ',')
    shipping_cost = format(shipping_cost, ',')
    extra_shipping_cost = format(extra_shipping_cost, ',')
    mileage_use = format(mileage_use, ',')
    deposit_use = format(deposit_use, ',')
    amount_to_pay = format(amount_to_pay, ',')

    html = html.replace('{$total_product_price}', str(total_product_price)) \
        .replace('{$discount_price}', str(total_sale_price)).replace('{$shipping_cost}', str(shipping_cost)) \
        .replace('{$extra_shipping_cost}', str(extra_shipping_cost)) \
        .replace('{$mileage_use}', str(mileage_use)).replace('{$deposit_use}', str(deposit_use)) \
        .replace('{$amount_to_pay}', str(amount_to_pay))

    soup = BeautifulSoup(html, "html.parser")
    if total_sale_price == '0':
        soup.find('tr', id="discount_price").decompose()
        html = str(soup)

    if shipping_cost == '0':
        soup.find('tr', id="shipping_cost").decompose()
        html = str(soup)

    if extra_shipping_cost == '0':
        soup.find('tr', id="extra_shipping_cost").decompose()
        html = str(soup)

    if mileage_use == '0':
        soup.find('tr', id="maileage_use").decompose()
        title = u'다노샵에서 주문하신 내역이에요'

    html = html.replace('{$name}', name).replace('{$order_num}', order.num) \
        .replace('{$order_time}', str(order.reg_time)[:16])

    total_product_price = format(total_product_price, ',')
    total_sale_price = format(total_sale_price, ',')
    shipping_cost = format(shipping_cost, ',')
    extra_shipping_cost = format(extra_shipping_cost, ',')
    mileage_use = format(mileage_use, ',')
    deposit_use = format(deposit_use, ',')
    amount_to_pay = format(amount_to_pay, ',')

    html = html.replace('{$total_product_price}', str(total_product_price)) \
        .replace('{$discount_price}', str(total_sale_price)).replace('{$shipping_cost}', str(shipping_cost)) \
        .replace('{$extra_shipping_cost}', str(extra_shipping_cost)) \
        .replace('{$mileage_use}', str(mileage_use)).replace('{$deposit_use}', str(deposit_use)) \
        .replace('{$amount_to_pay}', str(amount_to_pay))

    soup = BeautifulSoup(html, "html.parser")
    if total_sale_price == '0':
        soup.find('tr', id="discount_price").decompose()
        html = str(soup)

    if shipping_cost == '0':
        soup.find('tr', id="shipping_cost").decompose()
        html = str(soup)

    if extra_shipping_cost == '0':
        soup.find('tr', id="extra_shipping_cost").decompose()
        html = str(soup)

    if mileage_use == '0':
        soup.find('tr', id="maileage_use").decompose()
        html = str(soup)

    if deposit_use == '0':
        soup.find('tr', id="deposit_use").decompose()
        html = str(soup)

    if receiver_tel == '':
        soup.find('tr', id="receiver_tel").decompose()
        html = str(soup)

    if shipping_memo == '':
        soup.find('tr', id="shipping_memo").decompose()
        html = str(soup)

    html = html.replace('{$main_pay_method}', main_pay_method_str)

    html = html.replace('{$receiver_name}', receiver_name).replace('{$receiver_phone}', receiver_phone) \
        .replace('{$receiver_tel}', receiver_tel).replace('{$zip_code}', zip_code) \
        .replace('{$zip_address}', zip_address).replace('{$address}', address) \
        .replace('{$shipping_memo}', shipping_memo)

    html = html.replace('{$product_html}', product_html)

    msg = html
    if order.member:
        email = order.member.email
    else:
        email = order.non_member.email

    send_email(title, msg, [email, ])
    html = str(soup)


    if deposit_use == '0':
        soup.find('tr', id="deposit_use").decompose()
        html = str(soup)

    if receiver_tel == '':
        soup.find('tr', id="receiver_tel").decompose()
        html = str(soup)

    if shipping_memo == '':
        soup.find('tr', id="shipping_memo").decompose()
        html = str(soup)

    html = html.replace('{$main_pay_method}', main_pay_method_str)

    html = html.replace('{$receiver_name}', receiver_name).replace('{$receiver_phone}', receiver_phone) \
        .replace('{$receiver_tel}', receiver_tel).replace('{$zip_code}', zip_code) \
        .replace('{$zip_address}', zip_address).replace('{$address}', address) \
        .replace('{$shipping_memo}', shipping_memo)

    html = html.replace('{$product_html}', product_html)

    msg = html
    if order.member:
        email = order.member.email
    else:
        email = order.non_member.email

    send_email(title, msg, [email, ])