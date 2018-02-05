# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from views import ContentListView, ContentDetailView, MemberJoinView, ServerStatusView, ContentLikeView, SendEmailView, AdminContentListView, AdminContentDetailView

# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

#   CSRF TOKEN
# router.register(r'^v1/server/status/$', ServerStatusView.as_view(), name="server_status"),

#   Category
# router.register(r'^v1/content/list/$', ContentListView.as_view(), name="main_product_view"),
# router.register(r'^v1/content/detail/$', ContentDetailView.as_view(), name="shop_product_detail_view"),

#   Member
# router.register(r'^v1/member/join/(?P<request_type>\w+)', SubscriptionRegisterView.as_view(), name="member_join"),

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.

# urlpatterns = [
#     url(r'^', include(router.urls)),
# ]
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# )

urlpatterns = [
    #   CSRF TOKEN
    url(r'^v1/server/status/$', ServerStatusView.as_view(), name="server_status"),

    #   Category
    url(r'^v1/content/list/$', ContentListView.as_view(), name="main_product_view"),
    url(r'^v1/content/detail/$', ContentDetailView.as_view(), name="shop_product_detail_view"),
    url(r'^v1/member/join/$', MemberJoinView.as_view(), name="shop_product_detail_view"),
    url(r'^v1/content/like/$', ContentLikeView.as_view(), name="shop_product_detail_view"),
    url(r'^v1/send/email/$', SendEmailView.as_view(), name="shop_product_detail_view"),

    #   Admin
    url(r'^v1/admin/content/list/$', AdminContentListView.as_view(), name="main_product_view"),
    url(r'^v1/admin/content/detail/post/$', AdminContentDetailView.as_view(), name="main_product_view"),


    #   Member
    # url(r'^v1/member/join/(?P<request_type>\w+)', SubscriptionRegisterView.as_view(), name="member_join"),
]