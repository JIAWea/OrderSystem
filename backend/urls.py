
from django.urls import re_path
from backend.api import views, accounts

urlpatterns = [

    # 系统用户
    re_path('^admin/list/$', accounts.admin_list, name='admin_list'),
    re_path('^admin/view/$', accounts.admin_list_data, name='admin_view'),
    re_path('^admin/add/$', accounts.admin_add, name='admin_add'),
    re_path('^admin/delete/(?P<pk>\d+)$', accounts.admin_delete, name='admin_delete'),
    re_path('^admin/delete/multiple/$', accounts.admin_mulit_del, name='admin_mulit_del'),
    re_path('^admin/update/(?P<pk>\d+)$', accounts.admin_update, name='admin_update'),
    re_path('^admin/update/status/(?P<pk>\d+)$', accounts.admin_status, name='admin_status'),
    re_path('^admin/update/password/set/$', accounts.admin_setpasswd, name='pudate_admin_ban'),
    re_path('^admin/update/password/change/$', accounts.admin_change_passwd, name='pudate_admin_ban'),
    re_path('^admin/role/(?P<pk>\d+)$', accounts.admin_role, name='admin_role'),

    # 角色
    re_path('^role/list/$', accounts.role_list, name='permission_role'),
    re_path('^role/view/$', accounts.role_view, name='role_view'),
    re_path('^role/add/$', accounts.role_add, name='role_add'),
    re_path('^role/edit/(?P<pk>\d+)$', accounts.role_edit, name='role_edit'),
    re_path('^role/delete/(?P<pk>\d+)$', accounts.role_delete, name='role_delete'),
    re_path('^role/delete/multiple/$', accounts.role_mulit_delete, name='role_mulit_delete'),

    # 买家
    re_path('^buyers/list/$', views.buyer_list, name='buyer_list'),
    re_path('^buyers/view/$', views.buyer_list_ajax, name='buyer_list_ajax'),
    re_path('^buyers/delete/(?P<pk>\d+)$', views.buyer_delete, name='buyer_delete'),
    re_path('^buyers/edit/(?P<pk>\d+)$', views.buyer_list_edit, name='buyer_list_edit'),
    re_path('^buyers/edit/detail/(?P<pk>\d+)$', views.buyer_list_detail, name='buyer_list_detail'),
    re_path('^buyers/get/search/select/$', views.get_search_select, name='get_search_select'),

    re_path('^buyers/device/edit/$', views.BuyerDeviceEdit.as_view(), name='buyer_device_edit'),
    re_path('^buyers/buyer/edit/$', views.BuyerBuyerEdit.as_view(), name='buyer_buyer_edit'),
    re_path('^buyers/family/edit/$', views.BuyerFamilyEdit.as_view(), name='buyer_family_edit'),
    re_path('^buyers/internet/edit/$', views.BuyerInternetEdit.as_view(), name='buyer_internet_edit'),
    re_path('^buyers/card/edit/$', views.BuyerCardEdit.as_view(), name='buyer_card_edit'),
    re_path('^buyers/member/edit/$', views.BuyerMemberEdit.as_view(), name='buyer_member_edit'),
    re_path('^buyers/address/edit/$', views.BuyerAddressEdit.as_view(), name='buyer_address_edit'),
    re_path('^buyers/order/edit/$', views.BuyerOrderEdit.as_view(), name='buyer_order_edit'),

    # 订单
    re_path('^orders/list/$', views.order_list, name='order_list'),
    re_path('^orders/view/$', views.order_view, name='order_view'),
    re_path('^orders/delete/(?P<pk>\d+)$', views.order_delete, name='order_delete'),
    re_path('^orders/edit/(?P<pk>\d+)$', views.order_list_edit, name='order_list_edit'),
    re_path('^orders/edit/detail/(?P<pk>\d+)$', views.order_detail, name='order_detail'),
    re_path('^orders/edit/$', views.OrderEdit.as_view(), name='order_detail_edit'),
    re_path('^orders/get/search/select/$', views.get_orders_search_select, name='get_orders_search_select'),

    # 买家导入导出
    re_path('^buyers/import/$', views.buyer_import, name='buyer_import'),
    re_path('^buyers/export/$', views.buyer_export, name='buyer_export'),

    # 任务订单导入导出
    re_path('^orders/import/$', views.order_import, name='order_import'),
    re_path('^orders/export/$', views.order_export, name='order_export'),

    re_path('^index/$', views.index, name='index')
]
