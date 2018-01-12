# -*- coding: utf-8 -*-
"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'danoshop_server.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'danoshop_server.dashboard.CustomAppIndexDashboard'

by Jongseok.
    reason: No module named dashboard
    this file move to danoshop/ from danoshop_server/

"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for danoshop_server.
    """

    title = 'Danoshop Dashboard'
    columns = 3

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            # draggable=False,
            # deletable=False,
            #collapsible=False,
            collapsible=True,
            draggable=True,
            deletable=True,
            children=[
                [_('Return to site'), '/'],
                [_('Change password'),
                 reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ]
        ))


        for c in context:
            if 'user' in c:
                user = c['user']
                break

        if 'open_platform' in user.account:
            self.children.append(modules.ModelList(
                # title=u'Order - models..나..',
                _(u'주문 메뉴'),
                models=['libs.submodels.order.*', ],
            ))

        else:
            '''
            # append an app list module for "Applications"
            self.children.append(modules.AppList(
                _('Applications'),
                exclude=('django.contrib.*', 'libs.submodels.product.*', ),
            ))
            '''
            self.children.append(modules.ModelList(
                # title=u'Order - models..나..',
                _(u'주문 메뉴'),
                models=[
                    'libs.submodels.order.Order',
                    'libs.submodels.order.OrderItem',
                    'libs.submodels.order.OrderItemForDelivery',
                    'libs.submodels.order.DeliveryPauseDate',
                ],
            ))

            self.children.append(modules.ModelList(
                # title=u'Order - models..나..',
                _(u'네이버페이 관리 메뉴'),
                models=[
                    'libs.submodels.npay_order.NpayRecallRequest',
                    'libs.submodels.npay_order.NpayCancelRequest',
                    'libs.submodels.npay_order.NpayExchangeRequest',
                ],
            ))

            self.children.append(modules.ModelList(
                _(u'상품 메뉴'),
                models=['libs.submodels.product.*', ],
                exclude=[
                    'libs.submodels.product.ProductDetail',
                    'libs.submodels.product.ProductOptionGroup',
                    'libs.submodels.product.ProductOption',
                ],
            ))

            self.children.append(modules.ModelList(
                _(u'회원 메뉴'),
                models=['libs.submodels.member.*', ],
                exclude=[
                    'libs.submodels.member.MemberPoint',
                    'libs.submodels.member.MemberBoard',
                ],
            ))

            self.children.append(modules.ModelList(
                _(u'회원 Point'),
                models=['libs.submodels.member_point.*', ],
            ))

            self.children.append(modules.ModelList(
                _(u'프로모션'),
                models=['libs.submodels.promotion.*', ],
            ))

            self.children.append(modules.ModelList(
                _(u'샵 관리'),
                models=['libs.submodels.shop.*', ],
            ))

            self.children.append(modules.ModelList(
                _(u'게시판'),
                models=['libs.submodels.board.*', ],
                exclude=[
                    'libs.submodels.board.Comment',
                ],
            ))

            self.children.append(modules.ModelList(
                _(u'결제'),
                models=['libs.submodels.payment.*', ],
            ))

            # append an app list module for "Administration"
            self.children.append(modules.AppList(
                _('Administration'),
                models=('django.contrib.*',),
            ))

            # append a recent actions module
            self.children.append(modules.RecentActions(_('Recent Actions'), 5))

            # append a feed module
            self.children.append(modules.Feed(
                _('Latest Django News'),
                feed_url='http://www.djangoproject.com/rss/weblog/',
                limit=5
            ))

            # append another link list module for "support".
            self.children.append(modules.LinkList(
                _('Support'),
                children=[
                    {
                        'title': _('Django documentation'),
                        'url': 'http://docs.djangoproject.com/',
                        'external': True,
                    },
                    {
                        'title': _('Django "django-users" mailing list'),
                        'url': 'http://groups.google.com/group/django-users',
                        'external': True,
                    },
                    {
                        'title': _('Django irc channel'),
                        'url': 'irc://irc.freenode.net/django',
                        'external': True,
                    },
                ]
            ))

            self.children.append(modules.ModelList(
                    _('통계'),
                    models=[
                        'libs.submodels.order.PaymentStats',
                        ],
                    ))

            self.children.append(modules.ModelList(
                    _('배치작업'),
                    models=[
                        'libs.submodels.batch.Batch',
                        ],
                    ))

class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for danoshop_server.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('App Index - Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
