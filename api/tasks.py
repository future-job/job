# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# BASE_URL = getattr(settings, 'BASE_URL')

import requests
import json
from djcelery import celery

def send_email(title, msg, to):
    """
    :param title: 메일 제목
    :param msg: 메일 메시지
    :param to: 수신자 = ['mail_1', ...]
    :return: x
    """

    # if '127.0.0.1' in BASE_URL:
    #     # task_send_email(title, msg, to)
    #     print 'local not send'
    #     pass
    # else:
    task_send_email(title, msg, to)
    print 'SEND EMAIL'


# @celery.task
def task_send_email(title, msg, emaillist):
    print 'IN SEND EMAIL', emaillist
    recipient_variables = {}
    # to 에 한사람의 이메일 주소만 보이게 하기 위한 코드
    for i, email in enumerate(emaillist):
        print i, email
        recipient_variables[email] = {}
        recipient_variables[email]['i'] = i
    print "SENDING EMAIL"
    requests.post(
        "https://api.mailgun.net/v3/mg.future-job.net/messages",
        auth=("api", "key-def9f5a1efbd103df0543c8d87e86c57"),
        data={"from": "퓨처잡 <info@future-job.net>",
              "to": [','.join(emaillist)],
              "subject": title,
              "html": msg,
              "recipient-variables": (json.dumps(recipient_variables)),
              })

    print 'DONE'
    return
