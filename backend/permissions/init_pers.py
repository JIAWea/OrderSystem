from OrderSystem import settings


def init_permission(request, current_user):
    """
    用户权限的初始化
    :param current_user: 当前用户对象
    :param request: 请求相关所有数据
    :return:
    """
    # 2. 权限信息初始化
    # 根据当前用户信息获取此用户所拥有的所有权限，并放入session。
    # 当前用户所有权限
    permission_queryset = current_user.roles.\
        values('permissions__url', 'permissions__name', 'permissions__menu_id').distinct()

    # 用户权限url列表，--> 用于中间件验证用户权限
    permission_url_list = []

    # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]
    permission_menu_list = []

    for item in permission_queryset:
        permission_url_list.append(item['permissions__url'])
        if item['permissions__menu_id']:
            temp = {"title": item['permissions__name'],
                    "url": item["permissions__url"],
                    "menu_id": item["permissions__menu_id"]}
            permission_menu_list.append(temp)

    # 保存用户权限url列表
    request.session[settings.PERMISS_SESSION_KEY] = permission_url_list

    # 保存 权限菜单 和所有 菜单；用户登录后作菜单展示用
    # menu_list = list(Menu.objects.values('id', 'title', 'parent_id'))
    # request.session[settings.SESSION_MENU_KEY] = {
    #     settings.ALL_MENU_KEY: menu_list,
    #     settings.PERMISSION_MENU_KEY: permission_menu_list,
    # }
