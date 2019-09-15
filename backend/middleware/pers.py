import re

from OrderSystem import settings
from django.shortcuts import redirect, HttpResponse
from django.http import HttpResponseNotAllowed, JsonResponse
from django.utils.deprecation import MiddlewareMixin


class HttpHasNoPermission(HttpResponse):
    status_code = 403


class PersMiddleware(MiddlewareMixin):
    """
    检查用户的url请求是否是其权限范围内
    """
    def process_request(self, request):
        request_url = request.path_info
        permission_url = request.session.get(settings.PERMISS_SESSION_KEY)
        # print('访问url',request_url)
        # print('权限--',permission_url)

        # 如果请求url在白名单，放行
        for url in settings.SAFE_URL:
            if re.match(url, request_url):
                return None

        # 如果未取到permission_url, 重定向至登录；为了可移植性，将登录url写入配置
        if not permission_url:
            return redirect(settings.LOGIN_URL)

        # 循环permission_url，作为正则，匹配用户request_url
        # 正则应该进行一些限定，以处理：/user/ -- /user/add/匹配成功的情况
        flag = False
        for url in permission_url:
            url_pattern = settings.REGEX_URL.format(url=url)
            if re.match(url_pattern, request_url):
                flag = True
                break
        if flag:
            return None
        else:
            return HttpHasNoPermission("无此权限，请联系管理员")
