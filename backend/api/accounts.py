import json

from OrderSystem.settings import DEFAULT_PASSWORD
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.http import JsonResponse, HttpResponseBadRequest
from backend.models import BackendUser, Role, Permission
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from backend.permissions.init_pers import init_permission


def ac_login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        cookie_expires = request.POST.get("remanber")

        # 自定制验证,源码在backend.auth文件下，主要是进行选择数据库进行验证
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            init_permission(request, user)
            if cookie_expires:
                request.session.set_expiry(604800)      # 7天内免登陆
            return redirect(request.GET.get('next', '/backend/buyers/list/'))
        else:
            return render(request, 'login.html', {'error_msg': "用户名或密码错误!"})
    return render(request, 'login.html')


def ac_logout(request):
    """
    退出登录
    :param request:
    :return:
    """
    logout(request)
    return redirect('/login')


@login_required
def chenge_password(request):
    """
    后台管理页面用户修改密码
    :param request:
    :return:
    """
    user = request.user
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        repeat_password = request.POST.get('repeat_password', '').strip()

        # 检查旧密码是否正确
        if user.check_password(old_password):
            if not new_password:
                return JsonResponse({'err_msg': '新密码不能为空', })
            elif new_password != repeat_password:
                return JsonResponse({'err_msg': '两次密码不一致', })
            else:
                user.set_password(new_password)
                user.save()
                return redirect("/logout")
        else:
            return JsonResponse({'err_msg': '原密码输入错误', })


@login_required
def backenduser_add(request):
    """
    添加新管理员
    :param request:
    :return:
    """
    user = request.user
    response = {}
    if request.method == "POST":
        if user.is_authenticated:
            content = str(request.body, encoding='utf-8')
            data = json.loads(content)                      # 转为字典类型

            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            repeat_password = data.get('repeat_password')

            if username and password and repeat_password:
                if password != repeat_password:
                    return JsonResponse({'err_msg': '密码不一致'})
                exist_user = BackendUser.objects.filter(name=username).exists()
                if exist_user:
                    response['err_msg'] = '该用户名已存在'
                    return JsonResponse(response)

                BackendUser.objects.create_user(name=username, email=email, password=password)
                response['err_msg'] = '添加成功'

                return JsonResponse(response)
            else:
                return JsonResponse({'err_msg': '用户名或密码不能为空'})
        else:
            return JsonResponse({'err_msg': '只有超级管理员才能添加管理员'})


# 管理员列表
@login_required
def admin_list(request):
    return render(request, 'admin_list.html')


# 管理员列表数据
@login_required
def admin_list_data(request):
    data_list = []
    queryset = BackendUser.objects.all()
    for item in queryset:
        roles_list = []
        for i in item.roles.values('name'):
            roles_list.append(i['name'])
        roles_list = ','.join(roles_list) if roles_list else ''

        data_list.append({
            'id': item.id,
            'name': item.name,
            'email': item.email,
            'role': roles_list,
            'status': '已启用' if item.is_active else '已禁用',
            'last_login': item.last_login.strftime("%m/%d/%Y %H:%M:%S") if item.last_login else '',
        })

    return JsonResponse({
        'code': 0,
        'count': queryset.count(),
        'data': data_list
    })


# 角色页面
@login_required
def role_list(request):
    return render(request, 'role_list.html')


# 角色列表
@login_required
def role_view(request):
    if request.method == "GET":
        limit = request.GET.get('limit')
        current_page = request.GET.get('page', 1)

        roles = Role.objects.all().order_by('-id')
        pagination = Paginator(roles, limit)
        queryset = pagination.page(current_page).object_list

        data = []
        for obj in queryset:
            data.append({
                'id': obj.id,
                'name': obj.name,
                'create_time': obj.create_time.strftime("%m/%d/%Y %H:%M:%S"),
            })

        return JsonResponse({
            'code': 0,
            'count': 1,
            'data': data
        })
    else:
        return HttpResponseBadRequest("请求错误")


# 角色编辑
@login_required
def role_edit(request, pk):
    if request.method == "GET":
        # 所有权限
        pers_queryset = Permission.objects.all()
        pers_list = []
        for obj in pers_queryset:
            pers_list.append({
                "id": obj.id,
                "name": obj.name,
                "pid": obj.parents_id if obj.parents_id else 0
            })

        # 拥有权限
        ids = []
        has_role = Role.objects.filter(pk=pk).values("permissions__id", "permissions__parents_id").distinct()
        for role in has_role:
            ids.append(role['permissions__id'])
            if role['permissions__parents_id'] not in ids:
                ids.append(role['permissions__parents_id'])
        return JsonResponse({
            "code": 0,
            "msg": "获取成功",
            "data": {
                "list": pers_list,
                "checkedId": ids
            }
        })
    if request.method == "POST":
        data = json.loads(request.POST.get('data'))
        name = data.get('name')
        pers = json.loads(request.POST.get('pers'))
        if not pers:
            return JsonResponse({'status': 400, 'msg': '权限不能为空'})
        obj = Role.objects.filter(pk=pk).first()
        obj.name = name
        obj.permissions.set(pers)
        obj.save()
        return JsonResponse({'status': 200, 'msg': '编辑成功'})


# 添加角色
@login_required
def role_add(request):
    if request.method == "GET":
        pers_queryset = Permission.objects.all()
        pers_list = []
        for obj in pers_queryset:
            pers_list.append({
                "id": obj.id,
                "name": obj.name,
                "pid": obj.parents_id if obj.parents_id else 0
            })
        return JsonResponse({
            "code": 0,
            "msg": "获取成功",
            "data": {
                "list": pers_list,
                "checkedId": None
            }
        })
    if request.method == "POST":
        data = json.loads(request.POST.get('data'))
        name = data.get('name')
        pers = json.loads(request.POST.get('pers'))
        if not pers:
            return JsonResponse({'status': 400, 'msg': '权限不能为空'})
        obj = Role.objects.create(name=name)
        obj.permissions.set(pers)
        obj.save()
        return JsonResponse({'status': 200, 'msg': '编辑成功'})


# 删除角色
@login_required
def role_delete(request, pk):
    if request.method == "POST":
        Role.objects.filter(pk=pk).delete()
        return JsonResponse({'status': 200, 'msg': '删除成功'})
    else:
        return HttpResponseBadRequest("请求错误")


# 批量删除角色
@login_required
def role_mulit_delete(request):
    if request.method == "POST":
        data = request.POST.get('data')
        id_list = json.loads(data)
        Role.objects.filter(id__in=id_list).delete()
    return JsonResponse({'status': 200, 'msg': '删除成功'})


# 编辑管理员
@login_required
def admin_role(request, pk):
    has_role = []
    all_role = []
    try:
        admin = BackendUser.objects.get(pk=pk)
        roles = admin.roles.values('id', 'name')
        all_roles = Role.objects.values('id', 'name')
        for role in roles:
            has_role.append({
                'name': role['name'],
                'value': role['id']
            })
        for role in all_roles:
            all_role.append({
                'name': role['name'],
                'value': role['id']
            })
    except BackendUser.DoesNotExist:
        return HttpResponseBadRequest('找不到管理员')

    return JsonResponse({
        'status': 200,
        'data': has_role,
        'roles': all_role
    })


@login_required
def admin_add(request):
    if request.method == "GET":
        data = []
        all_roles = Role.objects.values('id', 'name')
        for role in all_roles:
            data.append({
                'name': role['name'],
                'value': role['id']
            })
        return JsonResponse({'status': 200, 'data': data})

    if request.method == "POST":
        content = request.POST.get('data')
        data = json.loads(content)
        username = data.get('username')
        password = data.get('passwd1')
        email = data.get('email', '')
        repeat_password = data.get('passwd2')
        if not data.get('role'):
            return JsonResponse({'status': 400, 'msg': '角色不能为空'})

        roles_list = data.get('role').split(',')

        if username and password and repeat_password:
            if password != repeat_password:
                return JsonResponse({'status': 400, 'msg': '密码不一致'})
            exist_user = BackendUser.objects.filter(name=username).exists()
            if exist_user:
                return JsonResponse({'status': 400, 'msg': '该用户名已经存在'})

            user = BackendUser.objects.create_user(
                name=username, email=email,
                password=password)
            user.roles.set(roles_list)
            user.save()
            return JsonResponse({'status': 200, 'msg': '添加成功'})
        else:
            return JsonResponse({'status': 400, 'msg': '用户名或密码不能为空'})


# 管理员编辑
def admin_update(request, pk):
    if request.method == "POST":
        content = request.POST.get('data')
        data = json.loads(content)
        name = data.get('username')
        email = data.get('email')
        role = data.get('role')
        if not role:
            return JsonResponse({'status': 400, 'msg': '角色不能为空'})
        roles_list = role.split(',')
        try:
            obj = BackendUser.objects.get(pk=pk)
            obj.name = name
            obj.email = email
            obj.roles.set(roles_list)
            obj.save()
        except BackendUser.DoesNotExist:
            return JsonResponse({'status': 400, 'msg': '管理员不存在'})
        return JsonResponse({'status': 200, 'msg': '编辑成功'})
    return HttpResponseBadRequest("请求失败")


# 更改管理员状态
def admin_status(request, pk):
    if request.method == "POST":
        status = request.POST.get("status")
        if request.user.is_authenticated:
            BackendUser.objects.filter(pk=pk).update(is_active=status)
            return JsonResponse({
                'status': 200
            })
        else:
            return JsonResponse({
                'status': 400,
                'msg': '您没有权限设置管理员状态'
            })
    else:
        return JsonResponse({'status': 400, 'msg': '错误请求'})


# 单个删除管理员
def admin_delete(request, pk):
    if request.method == "POST":
        if request.user.is_authenticated:
            BackendUser.objects.filter(pk=pk).delete()
            return JsonResponse({'status': 200, 'msg': '删除成功'})
        else:
            return JsonResponse({'status': 400, 'msg': '您没有权限删除管理员'})
    else:
        return JsonResponse({'status': 400, 'msg': '错误请求'})


# 批量删除管理员
def admin_mulit_del(request):
    if request.method == "POST":
        content = str(request.body, encoding='utf-8')  # 字符串
        result = json.loads(content)
        if request.user.is_authenticated:
            BackendUser.objects.filter(id__in=result).delete()
            return JsonResponse({'status': 200, 'msg': '删除成功'})
        else:
            return JsonResponse({'status': 400, 'msg': '您没有权限删除管理员'})
    else:
        return JsonResponse({'status': 400, 'msg': '错误请求'})


def admin_setpasswd(request):
    """
    重置管理员密码
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            content = str(request.body, encoding='utf-8')  # 字符串
            result = json.loads(content)
        except Exception:
            return JsonResponse({'status': 200, 'msg': '请发送JSON数据'})
        if request.user.is_authenticated:
            admin = BackendUser.objects.filter(id__in=result)
            for obj in admin:
                obj.set_password(DEFAULT_PASSWORD)
                obj.save()
            return JsonResponse({'status': 200, 'msg': '密码重置成功'})

        else:
            return JsonResponse({'status': 400, 'msg': '您没有权限重置管理员密码'})
    else:
        return JsonResponse({'status': 400, 'msg': '错误请求'})


def admin_change_passwd(request):
    """
    后台管理页面用户修改密码
    :param request:
    :return:
    """
    user = request.user
    # print(user)
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        repeat_password = request.POST.get('repeat_password', '').strip()

        # 检查旧密码是否正确
        if user.check_password(old_password):
            if not new_password:
                return JsonResponse({'err_msg': '新密码不能为空', })
            elif new_password != repeat_password:
                return JsonResponse({'err_msg': '两次密码不一致', })
            else:
                user.set_password(new_password)
                user.save()
                return redirect("/logout")
        else:
            return JsonResponse({'err_msg': '原密码输入错误', })


# 初始化数据库权限和菜单
def init_cmd(request):
    from OrderSystem.settings import DEBUG
    if DEBUG is True:
        from backend.models import Permission, Menu

        Menu.objects.create(id=1, title='设置')
        Menu.objects.create(id=2, title='订单信息管理')
        Menu.objects.create(id=3, title='买家信息管理')

        Permission.objects.create(id=1, name='用户管理', url='/backend/admin/list/', method='GET', menu_id=1,
                                  parents_id=None)
        Permission.objects.create(id=2, name='用户添加', url='/backend/admin/add/', method='POST', menu_id=None,
                                  parents_id=1)
        Permission.objects.create(id=3, name='用户删除', url='/backend/admin/edit/', method='POST', menu_id=None,
                                  parents_id=1)
        Permission.objects.create(id=4, name='用户修改', url='/backend/admin/delete/', method='POST', menu_id=None,
                                  parents_id=1)
        Permission.objects.create(id=5, name='用户查看', url='/backend/admin/view/', method='GET', menu_id=None,
                                  parents_id=1)

        Permission.objects.create(id=6, name='角色管理', url='/backend/role/list/', method='GET', menu_id=1,
                                  parents_id=None)
        Permission.objects.create(id=7, name='角色添加', url='/backend/role/add/', method='POST', menu_id=None,
                                  parents_id=6)
        Permission.objects.create(id=8, name='角色删除', url='/backend/role/delete/', method='POST', menu_id=None,
                                  parents_id=6)
        Permission.objects.create(id=9, name='角色修改', url='/backend/role/edit/', method='POST', menu_id=None,
                                  parents_id=6)
        Permission.objects.create(id=10, name='角色查看', url='/backend/role/view/', method='GET', menu_id=None,
                                  parents_id=6)

        Permission.objects.create(id=11, name='买家信息管理', url='/backend/buyers/list/', method='GET', menu_id=3,
                                  parents_id=None)
        Permission.objects.create(id=12, name='买家信息查看', url='/backend/buyers/view/', method='GET', menu_id=None,
                                  parents_id=11)
        Permission.objects.create(id=13, name='买家信息删除', url='/backend/buyers/delete/', method='POST', menu_id=None,
                                  parents_id=11)
        Permission.objects.create(id=14, name='买家搜索页信息修改', url='/backend/buyers/edit/', method='POST', menu_id=None,
                                  parents_id=11)
        Permission.objects.create(id=15, name='买家详情设备信息修改', url='/backend/buyers/device/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=16, name='买家详情买家信息修改', url='/backend/buyers/buyer/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=17, name='买家详情家庭信息修改', url='/backend/buyers/family/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=18, name='买家详情社交信息修改', url='/backend/buyers/internet/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=19, name='买家详情信用卡信息修改', url='/backend/buyers/card/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=20, name='买家详情会员状态修改', url='/backend/buyers/member/edit/', method='POST',
                                  menu_id=None, parents_id=11)
        Permission.objects.create(id=21, name='买家详情默认收货地址修改', url='/backend/buyers/address/edit/', method='POST',
                                  menu_id=None, parents_id=11)

        Permission.objects.create(id=22, name='订单信息管理', url='/backend/orders/list/', method='GET', menu_id=2,
                                  parents_id=None)
        Permission.objects.create(id=23, name='订单查看', url='/backend/orders/view/', method='GET', menu_id=None,
                                  parents_id=22)
        Permission.objects.create(id=24, name='订单删除', url='/backend/orders/delete/', method='POST', menu_id=None,
                                  parents_id=22)
        Permission.objects.create(id=25, name='订单详情修改', url='/backend/orders/edit/detail/', method='POST', menu_id=None,
                                  parents_id=22)
        Permission.objects.create(id=26, name='订单搜索页修改', url='/backend/orders/edit/', method='POST',
                                  menu_id=None, parents_id=22)
        print('初始化数据库...')
        return JsonResponse({'code': 'ok'})
    else:
        return HttpResponseBadRequest("错误请求")
