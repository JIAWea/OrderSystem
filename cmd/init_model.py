import os
import datetime

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrderSystem.settings')

application = get_wsgi_application()


from backend.models import Permission, Menu

Menu.objects.create(id=1, name='设置')
Menu.objects.create(id=2, name='订单信息管理')
Menu.objects.create(id=3, name='买家信息管理')

Permission.objects.create(id=1, name='用户管理', url='/backend/admin/list/', method='GET', menu_id=1, parents_id=None)
Permission.objects.create(id=2, name='用户添加', url='/backend/admin/add/', method='POST', menu_id=None, parents_id=1)
Permission.objects.create(id=3, name='用户删除', url='/backend/admin/edit/', method='POST', menu_id=None, parents_id=1)
Permission.objects.create(id=4, name='用户修改', url='/backend/admin/delete/', method='POST', menu_id=None, parents_id=1)
Permission.objects.create(id=5, name='用户查看', url='/backend/admin/view/', method='GET', menu_id=None, parents_id=1)

Permission.objects.create(id=6, name='角色管理', url='/backend/role/list/', method='GET', menu_id=1, parents_id=None)
Permission.objects.create(id=7, name='角色添加', url='/backend/role/add/', method='POST', menu_id=None, parents_id=6)
Permission.objects.create(id=8, name='角色删除', url='/backend/role/delete/', method='POST', menu_id=None, parents_id=6)
Permission.objects.create(id=9, name='角色修改', url='/backend/role/edit/', method='POST', menu_id=None, parents_id=6)
Permission.objects.create(id=10, name='角色查看', url='/backend/role/view/', method='GET', menu_id=None, parents_id=6)

Permission.objects.create(id=11, name='买家信息管理', url='/backend/buyers/list/', method='GET', menu_id=3, parents_id=None)
Permission.objects.create(id=12, name='买家信息查看', url='/backend/buyers/view/', method='GET', menu_id=None, parents_id=11)
Permission.objects.create(id=13, name='买家信息删除', url='/backend/buyers/delete/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=14, name='买家搜索页信息修改', url='/backend/buyers/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=15, name='买家详情设备信息修改', url='/backend/buyers/device/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=16, name='买家详情买家信息修改', url='/backend/buyers/buyer/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=17, name='买家详情家庭信息修改', url='/backend/buyers/family/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=18, name='买家详情社交信息修改', url='/backend/buyers/internet/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=19, name='买家详情信用卡信息修改', url='/backend/buyers/card/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=20, name='买家详情会员状态修改', url='/backend/buyers/member/edit/', method='POST', menu_id=None, parents_id=11)
Permission.objects.create(id=21, name='买家详情默认收货地址修改', url='/backend/buyers/address/edit/', method='POST', menu_id=None, parents_id=11)

Permission.objects.create(id=22, name='订单信息管理', url='/backend/orders/list/', method='GET', menu_id=2, parents_id=None)
Permission.objects.create(id=23, name='订单查看', url='/backend/orders/view/', method='GET', menu_id=None, parents_id=22)
Permission.objects.create(id=24, name='订单删除', url='/backend/orders/delete/', method='POST', menu_id=None, parents_id=22)
Permission.objects.create(id=25, name='订单详情修改', url='/backend/orders/detail/edit/', method='POST', menu_id=None, parents_id=22)
Permission.objects.create(id=26, name='订单搜索页修改', url='/backend/buyers/address/edit/', method='POST', menu_id=None, parents_id=22)


