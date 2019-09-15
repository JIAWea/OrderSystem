import os
import datetime
import json
import tempfile

from django.db import connection
from django.db.models import Count, Min, Max
from OrderSystem.settings import EXCEL_PATH
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from backend.models import BackendUser
from customer.models import Buyer, Order
from django.core.serializers import serialize
from backend.utils import str2date, get_tilde_splitted_date_range, str2int, file_iterator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from backend.xlsx_handler import buyers_handler, orders_handler
from backend.xlsx_writer import Writer as XlsxWriter
from django.utils.encoding import escape_uri_path
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@login_required
def index(request):
    return redirect('/backend/buyers/list/')


@login_required
def buyer_list(request):
    return render(request, 'buyers_list.html')


@login_required
def buyer_list_ajax(request):
    limit = request.GET.get('limit', 10)
    current_page = request.GET.get('page', 1)

    search_first_order_time = False
    search_comment_last_time = False
    search_valid_order = False
    search_review_count = False
    search_cc_total = False
    search_review_percent = False
    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)

    kwargs = {}
    condition = request.GET.get('condition')
    if condition:
        data = json.loads(condition)
        platform = data.get('platform')
        site = data.get('site')
        buyer_status = data.get('buyer_status')
        cc = data.get('cc')
        order_vaild = data.get('order_vaild')
        member_type = data.get('member_type')
        review = data.get('review')
        comment_percent = data.get('comment_percent')
        buyer_number = data.get('buyer_number')
        buyer_phone = data.get('buyer_phone')
        buyer_email = data.get('buyer_email')
        member_expiry_time = data.get('member_expiry_time')
        order_first_time = data.get('order_first_time')
        comment_last_time = data.get('comment_last_time')

        if platform:
            kwargs.update({
                'platform': platform
            })
        if site:
            kwargs.update({
                'buyer_site': site
            })
        if buyer_status:
            kwargs.update({
                'buyer_status': buyer_status
            })
        if member_type:
            kwargs.update({
                'member_type': member_type
            })
        if buyer_number:
            kwargs.update({
                'number': buyer_number
            })
        if buyer_phone:
            kwargs.update({
                'buyer_phone': buyer_phone
            })
        if platform:
            kwargs.update({
                'platform': platform
            })
        if buyer_email:
            kwargs.update({
                'buyer_email': buyer_email
            })
        if member_expiry_time:
            mx_start_time, mx_end_time = get_tilde_splitted_date_range(member_expiry_time)
            kwargs.update({
                'member_expiry_time__range': (mx_start_time, mx_end_time)
            })

        if order_first_time:
            start_time, end_time = get_tilde_splitted_date_range(order_first_time)
            search_first_order_time = True
        if comment_last_time:
            comment_last_time = str2date(comment_last_time)
            search_comment_last_time = True

        # Review数量（评论数量）
        if review:
            review = str2int(review)
            search_review_count = True
        # 累计CC金额权重
        if cc:
            cc = str2int(cc)
            search_cc_total = True
        # 累计有效订单
        if order_vaild:
            order_vaild = str2int(order_vaild)
            search_valid_order = True
        # 留评比
        if comment_percent:
            comment_percent = str2int(comment_percent)
            search_review_percent = True

    queryset_all = Buyer.objects.all().filter(**kwargs).order_by('-id')

    # ############ 筛选开始
    # 筛选首单时间
    if search_first_order_time is True:
        order_queryset = Order.objects.values('buyer__id').\
            annotate(count=Count('buyer__id'), min=Min('create_time')).\
            filter(min__range=(start_time, end_time))
        ids = [obj['buyer__id'] for obj in order_queryset]
        queryset_all = queryset_all.filter(id__in=ids)

    # 筛选最后留评时间
    if search_comment_last_time is True:
        review_last = Order.objects.values('buyer__id'). \
            annotate(max=Max('review_time')).\
            filter(max=comment_last_time)
        ids = [obj['buyer__id'] for obj in review_last]
        queryset_all = queryset_all.filter(id__in=ids)

    # Review数量
    if search_review_count is True:
        # review_count = Order.objects.values('buyer__id', 'review_type').filter(review_type='Review').\
        #     annotate(count=Count('review_type')). \
        #     filter(count__gt=review)
        # ids = [obj['buyer__id'] for obj in review_count]
        cursor = connection.cursor()
        sql = """
                SELECT buyer_id, CASE WHEN review_status != '未'  THEN COUNT(*) ELSE 0 END AS review_count
                FROM customer_order GROUP BY customer_order.buyer_id having review_count >= {}
            """.format(review)
        cursor.execute(sql)
        rows = cursor.fetchall()
        ids = [obj[0] for obj in rows]
        queryset_all = queryset_all.filter(id__in=ids)

    # 累计CC金额权重
    if search_cc_total is True:
        ids = []
        one_year_price = Order.objects.values('buyer__id').annotate(price_sum=Sum('purchase_price')). \
            filter(mode_payment='信用卡', create_time__gte=one_year_ago)
        for obj in one_year_price:
            if cc == 50 and int(obj['price_sum']) >= 50:
                ids.append(obj['buyer__id'])
            elif cc ==25 and 25 <= int(obj['price_sum']) < 50:
                ids.append(obj['buyer__id'])
            elif 0 < cc <25 and 0 < int(obj['price_sum']) < 25:
                ids.append(obj['buyer__id'])
            elif cc == 0 and int(obj['price_sum']) == 0:
                ids.append(obj['buyer__id'])
        queryset_all = queryset_all.filter(id__in=ids)

    # 累计有效订单
    if search_valid_order is True:
        valid_order = Order.objects.values('buyer__id').filter(order_status="正常").\
            annotate(count=Count('order_status')).filter(count__gte=order_vaild)
        ids = [obj['buyer__id'] for obj in valid_order]
        queryset_all = queryset_all.filter(id__in=ids)

    # 留评比 = Review数量/订单数量
    if search_review_percent is True:
        cursor = connection.cursor()
        sql = """
                SELECT res.buyer_id, CONCAT(ROUND(SUM(res.pl_count)/SUM(res.order_count) * 100, 2), '', '%') as percent
                FROM 
                (
                    SELECT buyer_id,
                    CASE 
                        WHEN review_status != '未' THEN COUNT(id) ELSE 0 END AS pl_count, 
                    COUNT(id) AS order_count 
                    FROM customer_order
                    GROUP BY buyer_id, review_status
                ) res
                GROUP BY res.buyer_id having percent >= {}
            """.format(comment_percent)
        cursor.execute(sql)
        rows = cursor.fetchall()
        ids = [obj[0] for obj in rows]
        queryset_all = queryset_all.filter(id__in=ids)
    # ############ 筛选结束

    pagination = Paginator(queryset_all, limit)
    queryset = pagination.page(current_page).object_list

    data = []

    for obj in queryset:
        # 会员过期时间
        member_expiry_time = obj.member_expiry_time.strftime("%m/%d/%Y")\
            if obj.member_expiry_time else None

        # 12月信用卡累计金额
        one_year_price = Order.objects.\
            filter(mode_payment='信用卡', buyer_number=obj.number, create_time__gt=one_year_ago).\
            aggregate(sum_year=Sum('purchase_price'))
        one_year_price = one_year_price.get('sum_year') if one_year_price.get('sum_year') else 0

        # 累计有效订单金额
        order_vaild_price = Order.objects.filter(buyer_number=obj.number, order_status='正常').\
            aggregate(price=Sum('purchase_price'))
        order_vaild_price = order_vaild_price.get('price')

        # Review数量
        review_count = Order.objects.exclude(review_status='未').filter(buyer_number=obj.number).count()

        # 留评比 = Review数量/订单数量
        order_count = Order.objects.filter(buyer_number=obj.number).count()
        if int(review_count) == 0 or int(order_count) == 0:
            review_percent = '0'
        else:
            review_percent = '{:.2f}%'.format(int(review_count) / int(order_count) * 100)

        # 首单时间
        order_first = Order.objects.filter(buyer_number=obj.number).aggregate(min=Min('create_time'))
        order_first_time = order_first['min'].strftime("%m/%d/%Y") \
            if order_first['min'] else None

        # 最后留评论时间
        review_last = Order.objects.filter(buyer_number=obj.number).\
            aggregate(max=Max('review_time'))
        review_last_time = review_last['max'].strftime("%m/%d/%Y") \
            if review_last['max'] else None

        data.append({
            'id': obj.id,
            'number': obj.number,
            'buyer_status': obj.buyer_status,
            'member_type': obj.member_type,
            'member_expiry_time': member_expiry_time,
            'buyer_phone': obj.buyer_phone,
            'buyer_email': obj.buyer_email,
            'one_year_price': one_year_price,
            'order_vaild_price': order_vaild_price if order_vaild_price else '0',
            'review_count': review_count,
            'review_percent': review_percent,
            'order_first_time': order_first_time,
            'review_last_time': review_last_time
        })

    return JsonResponse({
        'code': 0,
        'count': pagination.count,
        'data': data
    })


# 买家信息删除
@login_required
def buyer_delete(request, pk):
    if Buyer.objects.filter(pk=pk).exists():
        Buyer.objects.filter(pk=pk).delete()
        return JsonResponse({'status': 200, 'msg': '删除成功'})
    else:
        return HttpResponseBadRequest("删除失败,不存在此买家信息")


# 买家信息列表编辑
@login_required
def buyer_list_detail(request, pk):
    try:
        buyer_obj = Buyer.objects.filter(pk=pk)[0]
        if not buyer_obj:
            return render(request, '404.html')
    except IndexError:
        return render(request, '404.html')
    return render(request, 'buyers_detail.html', {'obj_id': buyer_obj.id, 'number': buyer_obj.number})


@login_required
def get_search_select(request):
    platform_list = []
    member_type_list = []
    buyer_site_list = []
    platform = Buyer.objects.values('platform').distinct()
    member_type = Buyer.objects.values('member_type').distinct()
    buyer_site = Buyer.objects.values('buyer_site').distinct()
    for obj in platform:
        platform_list.append(obj)
    for obj in member_type:
        member_type_list.append(obj)
    for obj in buyer_site:
        buyer_site_list.append(obj)
    return JsonResponse({
        'status': 200,
        'platform': platform_list,
        'member_type': member_type_list,
        'buyer_site_list': buyer_site_list
    })


@login_required
def get_orders_search_select(request):
    platform_list = []
    platform = Order.objects.values('platform').distinct()
    for obj in platform:
        platform_list.append(obj)

    return JsonResponse({
        'status': 200,
        'platform': platform_list,
    })


# 买家信息详细页
@login_required
def buyer_list_edit(request, pk):
    # 买家信息详细页信息
    if request.method == "GET":
        obj = Buyer.objects.filter(pk=pk)
        if not obj:
            return HttpResponseBadRequest("没有该买家号")

        # 直接序列化数据
        serialize_obj = serialize('json', obj)
        data = json.loads(serialize_obj)[0]['fields']

        if obj[0].member_apply_time:
            member_apply_time = obj[0].member_apply_time.strftime("%m/%d/%Y")
            data.update({'member_apply_time': member_apply_time})
        if obj[0].member_expiry_time:
            member_expiry_time = obj[0].member_expiry_time.strftime("%m/%d/%Y")
            data.update({'member_expiry_time': member_expiry_time})
        if obj[0].credit_card_expiry:
            credit_card_expiry = obj[0].credit_card_expiry.strftime("%m/%d/%Y")
            data.update({'credit_card_expiry': credit_card_expiry})
        if obj[0].order_time:
            order_time = obj[0].order_time.strftime("%m/%d/%Y")
            data.update({'order_time': order_time})
        if obj[0].order_finish_time:
            order_finish_time = obj[0].order_finish_time.strftime("%m/%d/%Y")
            data.update({'order_finish_time': order_finish_time})

        # 计算订单总金额，和累计CC金额
        total_money = Order.objects.filter(buyer=obj[0]).aggregate(sum=Sum('purchase_price'))
        total_money = total_money['sum'] if total_money['sum'] else 0
        one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        one_year_money = Order.objects.filter(buyer=obj[0], mode_payment='信用卡', create_time__gte=one_year_ago).\
            aggregate(sum=Sum('purchase_price'))
        one_year_money = one_year_money['sum'] if one_year_money['sum'] else 0
        data.update({'total_money': total_money, 'one_year_money': one_year_money})

        return JsonResponse({
            'code': 0,
            'count': 1,
            'data': data,
            'id': json.loads(serialize_obj)[0]['pk']
        })

    # 买家页面信息编辑
    if request.method == "POST":
        content = request.body.decode('utf-8')
        data = json.loads(content)
        number = data.get('number')
        buyer_status = data.get('buyer_status')
        member_status = data.get('member_status')
        member_expiry_time = data.get('member_expiry_time')
        buyer_phone = data.get('buyer_phone')
        buyer_email = data.get('buyer_email')

        if member_expiry_time:
            member_expiry_time = str2date(member_expiry_time)

        Buyer.objects.filter(pk=pk).update(
            number=number, buyer_status=buyer_status,
            member_status=member_status, member_expiry_time=member_expiry_time,
            buyer_phone=buyer_phone, buyer_email=buyer_email
        )
        return JsonResponse({
            "code": 0,
            "msg": "编辑成功"
        })


class BuyerDeviceEdit(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerDeviceEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        number = request.POST.get('number', '')
        ip = request.POST.get('ip', '')
        ip_name = request.POST.get('ip_name', '')
        ip_password = request.POST.get('ip_password', '')

        if not number and not pk:
            return HttpResponseBadRequest("没有改买家编号")

        Buyer.objects.filter(pk=pk).update(
            number=number, ip=ip,
            ip_name=ip_name, ip_password=ip_password)

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerBuyerEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerBuyerEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        pk = request.POST.get('id')
        # data = json.loads(request.POST.get('data'))
        platform = request.POST.get('platform', '')
        buyer_site = request.POST.get('buyer_site', '')
        buyer_name = request.POST.get('buyer_name', '')
        buyer_ua = request.POST.get('buyer_ua', '')
        buyer_status = request.POST.get('buyer_status', '')
        buyer_cookie = request.POST.get('buyer_cookie', '')
        buyer_phone = request.POST.get('buyer_phone', '')
        buyer_email = request.POST.get('buyer_email', '')
        buyer_email_password = request.POST.get('buyer_email_password', '')
        buyer_login_password = request.POST.get('buyer_login_password', '')

        if not pk:
            return HttpResponseBadRequest("没有该买家编号")

        Buyer.objects.filter(pk=pk).update(
            platform=platform, buyer_site=buyer_site,
            buyer_name=buyer_name, buyer_ua=buyer_ua,
            buyer_status=buyer_status, buyer_cookie=buyer_cookie,
            buyer_phone=buyer_phone, buyer_email=buyer_email,
            buyer_email_password=buyer_email_password, buyer_login_password=buyer_login_password)

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerFamilyEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerFamilyEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        partner_name = request.POST.get('partner_name', '')
        partner_email = request.POST.get('partner_email', '')
        partner_email_password = request.POST.get('partner_email_password', '')
        if not pk:
            return HttpResponseBadRequest("没有该买家号")

        Buyer.objects.filter(pk=pk).update(
            partner_name=partner_name, partner_email=partner_email,
            partner_email_password=partner_email_password)

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerInternetEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerInternetEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        facebook = request.POST.get('facebook', '')
        gmail = request.POST.get('gmail', '')
        twitter = request.POST.get('twitter', '')
        youtube = request.POST.get('youtube', '')
        if not pk:
            return HttpResponseBadRequest("没有该买家号")

        Buyer.objects.filter(pk=pk).update(
            facebook=facebook, gmail=gmail,
            twitter=twitter, youtube=youtube)

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerCardEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerCardEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        credit_card = request.POST.get('credit_card', '')
        credit_card_expiry = request.POST.get('credit_card_expiry', '')
        credit_card_cvv = request.POST.get('credit_card_cvv', '')
        credit_card_origin = request.POST.get('credit_card_origin', '')
        if not pk:
            return HttpResponseBadRequest("没有该买家编号")

        credit_card_expiry = str2date(credit_card_expiry) if credit_card_expiry else None

        try:
            Buyer.objects.filter(pk=pk).update(
                credit_card=credit_card, credit_card_expiry=credit_card_expiry,
                credit_card_cvv=credit_card_cvv, credit_card_origin=credit_card_origin)
        except ValidationError:
            return JsonResponse({'status': 400, 'msg': '请输入有效日期'})

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerMemberEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerMemberEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        member_status = request.POST.get('member_status', '')
        member_apply_time = request.POST.get('member_apply_time', '')
        member_expiry_time = request.POST.get('member_expiry_time', '')
        if not pk:
            return HttpResponseBadRequest("没有该买家编号")

        member_apply_time = str2date(member_apply_time) if member_apply_time else None

        member_expiry_time = str2date(member_expiry_time) if member_expiry_time else None


        try:
            Buyer.objects.filter(pk=pk).update(
                member_status=member_status, member_apply_time=member_apply_time,
                member_expiry_time=member_expiry_time)
        except ValidationError:
            return JsonResponse({'status': 400, 'msg': '请输入有效日期'})

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerAddressEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerAddressEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        address1 = request.POST.get('address1', '')
        city = request.POST.get('city', '')
        zip = request.POST.get('zip', '')
        state = request.POST.get('state', '')
        phones = request.POST.get('phones', '')
        if not pk:
            return HttpResponseBadRequest("没有改买家编号")

        Buyer.objects.filter(pk=pk).update(
            first_name=first_name, last_name=last_name,
            city=city, state=state,
            zip=zip, phones=phones,
            address1=address1)

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


class BuyerOrderEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BuyerOrderEdit, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # data = json.loads(request.POST.get('data'))
        pk = request.POST.get('id')
        order_time = request.POST.get('order_time', '')
        order_number = request.POST.get('order_number', '')
        order_finish_time = request.POST.get('order_finish_time', None)
        order_task_type = request.POST.get('order_task_type', '')
        if not pk:
            return HttpResponseBadRequest("没有该买家编号")
        # obj = Buyer.objects.filter(pk=pk)[0]

        order_time = str2date(order_time) if order_time else None
        if not order_time:
            return JsonResponse({'status': 400, 'msg': '任务时间不能为空'})

        order_finish_time = str2date(order_finish_time) if order_finish_time else None

        try:
            Buyer.objects.filter(pk=pk).update(
                order_time=order_time, order_task_type=order_task_type,
                order_finish_time=order_finish_time, order_number=order_number)
        except ValidationError:
            return JsonResponse({'status': 400, 'msg': '请输入有效日期'})

        return JsonResponse({'status': 200, 'msg': '编辑成功'})


@login_required
def order_list(request):
    return render(request, 'orders_list.html')


# 订单首页
@login_required
def order_view(request):
    limit = request.GET.get('limit', 10)
    current_page = request.GET.get('page', 1)
    queryset = Order.objects.all().order_by('-order_time').order_by('-id')

    kwargs = {}
    condition = request.GET.get('condition')
    if condition:
        data = json.loads(condition)
        platform = data.get('platform')
        site = data.get('site')
        manager = data.get('manager')
        store_id = data.get('store_id')
        target_asin = data.get('target_asin')
        member_type = data.get('member_type')
        buyer_number = data.get('buyer_number')
        buyer_phone = data.get('buyer_phone')
        buyer_email = data.get('buyer_email')
        order_discount = data.get('order_discount')
        purchase_price = data.get('purchase_price')
        buyer_status = data.get('buyer_status')
        review_status = data.get('review_status')
        order_status = data.get('order_status')
        facebook_status = data.get('facebook_status')

        review_time = data.get('review_time')
        feedback_time = data.get('feedback_time')
        order_time = data.get('order_time')

        kwargs = {}
        if review_status:
            kwargs.update({
                'review_status': review_status
            })
        if order_status:
            kwargs.update({
                'order_status': order_status
            })
        if facebook_status:
            kwargs.update({
                'facebook_status': facebook_status
            })
        if order_discount:
            kwargs.update({
                'order_discount': order_discount
            })
        if purchase_price:
            kwargs.update({
                'purchase_price': purchase_price
            })
        if platform:
            kwargs.update({
                'platform': platform
            })
        if site:
            kwargs.update({
                'site': site
            })
        if buyer_number:
            kwargs.update({
                'buyer_number': buyer_number
            })
        if manager:
            kwargs.update({
                'manager': manager
            })
        if store_id:
            kwargs.update({
                'store_id': store_id
            })
        if target_asin:
            kwargs.update({
                'target_asin': target_asin
            })

        # 买家信息筛选
        if buyer_status:
            queryset = queryset.filter(buyer__buyer_status=buyer_status)
        if member_type:
            queryset = queryset.filter(buyer__member_type=member_type)
        if buyer_phone:
            queryset = queryset.filter(buyer__buyer_phone=buyer_phone)
        if buyer_email:
            queryset = queryset.filter(buyer__buyer_email=buyer_email)

        # 时间筛选
        if review_time:
            mx_start_time, mx_end_time = get_tilde_splitted_date_range(review_time)
            print('review_time:', mx_start_time, mx_end_time)
            queryset = queryset.filter(review_time__range=(mx_start_time, mx_end_time))
        if feedback_time:
            mx_start_time, mx_end_time = get_tilde_splitted_date_range(feedback_time)
            print('feedback_time:', mx_start_time, mx_end_time)
            queryset = queryset.filter(feedback_time__range=(mx_start_time, mx_end_time))
        if order_time:
            mx_start_time, mx_end_time = get_tilde_splitted_date_range(order_time)
            print('order_time:', mx_start_time, mx_end_time)
            queryset = queryset.filter(order_time__range=(mx_start_time, mx_end_time))

    queryset_all = queryset.filter(**kwargs)

    pagination = Paginator(queryset_all, limit)
    queryset = pagination.page(current_page).object_list

    data = []
    for obj in queryset:
        buyer_obj = Buyer.objects.filter(number=obj.buyer_number).first()
        buyer_status = buyer_obj.buyer_status if buyer_obj else ''
        member_type = buyer_obj.member_type if buyer_obj else ''
        buyer_phone = buyer_obj.buyer_phone if buyer_obj else ''
        buyer_email = buyer_obj.buyer_email if buyer_obj else ''

        data.append({
            'id': obj.id,
            'buyer_number': obj.buyer_number,
            'platform': obj.platform,
            'site': obj.site,
            'manager': obj.manager,
            'order_number': obj.order_number,
            'target_asin': obj.target_asin,
            'store_id': obj.store_id,
            'link_asin': obj.link_asin,
            'goods_price': obj.goods_price,
            'purchase_price': obj.purchase_price,
            'order_discount': obj.order_discount,
            'review_status': obj.review_status,
            'feedback_status': obj.feedback_status,
            'order_time': obj.order_time.strftime("%m/%d/%Y") if obj.order_time else '',
            'review_time': obj.review_time.strftime("%m/%d/%Y") if obj.review_time else '',
            'feedback_time': obj.feedback_time.strftime("%m/%d/%Y") if obj.feedback_time else '',

            'buyer_status': buyer_status,
            'member_type': member_type,
            'buyer_phone': buyer_phone,
            'buyer_email': buyer_email,
        })

    return JsonResponse({
        'code': 0,
        'count': pagination.count,
        'data': data
    })


# 订单信息删除
@login_required
def order_delete(request, pk):
    if Order.objects.filter(pk=pk).exists():
        Order.objects.filter(pk=pk).delete()
        return JsonResponse({'status': 200, 'msg': '删除成功'})
    else:
        return HttpResponseBadRequest("删除失败,不存在此买家信息")


# 订单页面信息编辑
@login_required
def order_list_edit(request, pk):

    if request.method == "POST":
        content = request.body.decode('utf-8')
        data = json.loads(content)

        buyer_number = data.get('buyer_number')
        platform = data.get('platform')
        site = data.get('site')
        manager = data.get('manager')
        order_number = data.get('order_number')
        target_asin = data.get('target_asin')
        store_id = data.get('store_id')
        link_asin = data.get('link_asin')
        goods_price = data.get('goods_price')
        purchase_price = data.get('purchase_price')
        review_status = data.get('review_status')
        feedback_status = data.get('feedback_status')

        review_time = data.get('e_review_time')
        feedback_time = data.get('e_feedback_time')
        order_time = data.get('e_order_time')

        review_time = str2date(review_time) if review_time else None
        feedback_time = str2date(feedback_time) if feedback_time else None

        if not order_time:
            return JsonResponse({"code": 1, "msg": "订单时间不能为空"})
        order_time = str2date(order_time)

        Order.objects.filter(pk=pk).update(
            buyer_number=buyer_number, platform=platform,
            site=site, manager=manager,
            order_number=order_number, target_asin=target_asin,
            store_id=store_id, link_asin=link_asin,
            goods_price=goods_price, purchase_price=purchase_price,
            review_status=review_status, feedback_status=feedback_status,
            review_time=review_time, feedback_time=feedback_time,
            order_time=order_time
        )
        return JsonResponse({
            "code": 0,
            "msg": "编辑成功"
        })


# 订单详情页
@login_required
def order_detail(request, pk):
    try:
        obj = Order.objects.filter(pk=pk).first()
        if not obj:
            return render(request, '404.html')
    except IndexError:
        return render(request, '404.html')
    return render(request, 'orders_detail.html', {'obj_id': obj.id, 'number': obj.buyer_number})


# 订单编辑
class OrderEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(OrderEdit, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        pk = request.GET.get('id')
        obj = Order.objects.filter(pk=pk)[0]
        if not obj:
            return HttpResponseBadRequest("没有该订单")
        buyer_obj = Buyer.objects.filter(number=obj.buyer_number).first()
        buyer_status = buyer_obj.buyer_status if buyer_obj else ''
        credit_card_expiry = obj.buyer.credit_card_expiry.strftime("%m/%d/%Y") \
            if obj.buyer.credit_card_expiry else ''

        return JsonResponse({
            'code': 0,
            'data': {
                'site': obj.site,
                'manager': obj.manager,
                'order_number': obj.order_number,
                'select_key': obj.select_key,
                'share_type': obj.share_type,
                'create_time': obj.create_time.strftime("%m/%d/%Y") if obj.create_time else '',
                'target_asin': obj.target_asin,
                'target_goods_title': obj.target_goods_title,
                'order_status': obj.order_status,
                'store_id': obj.store_id,
                'goods_price': obj.goods_price,
                'purchase_price': obj.purchase_price,
                'discount_code': obj.discount_code,
                'order_discount': obj.order_discount,
                'mode_payment': obj.mode_payment,
                'credit_card': obj.buyer.credit_card,
                'credit_card_expiry': credit_card_expiry,
                'card_cvv': obj.buyer.credit_card_cvv,
                'credit_card_origin': obj.buyer.credit_card_origin,
                'first_name': obj.first_name,
                'last_name': obj.last_name,
                'address1': obj.address1,
                'city': obj.city,
                'state': obj.state,
                'zip': obj.zip,
                'phones': obj.phones,
                'review_title': obj.review_title,
                'review_content': obj.review_content,
                'review_time': obj.review_time.strftime("%m/%d/%Y") if obj.review_time else '',
                'feedback_title': obj.feedback_title,
                'feedback_time': obj.feedback_time.strftime("%m/%d/%Y") if obj.feedback_time else '',
                'review_status': obj.review_status,
                'feedback_status': obj.feedback_status,
                'buyer_status': buyer_status,       # 买家Buyer状态
            }
        })

    def post(self, request):
        pk = request.POST.get('id')
        order_number = request.POST.get('order_number', '')
        order_status = request.POST.get('order_status', '')
        buyer_status = request.POST.get('buyer_status', '')
        review_status = request.POST.get('review_status', '')
        feedback_status = request.POST.get('feedback_status', '')
        create_time = request.POST.get('create_time', '')
        review_time = request.POST.get('review_time', '')
        feedback_time = request.POST.get('feedback_time', '')

        if not pk and not order_number:
            return HttpResponseBadRequest("没有此订单")
        # buyer_status = '1',

        create_time = str2date(create_time) if create_time else None
        if not create_time:
            return JsonResponse({'status': 400, 'msg': '购买时间不能为空'})
        review_time = str2date(review_time) if review_time else None
        feedback_time = str2date(feedback_time) if feedback_time else None

        try:
            Order.objects.filter(id=pk).update(
                create_time=create_time,
                review_status=review_status, feedback_status=feedback_status,
                review_time=review_time, feedback_time=feedback_time,
                order_status=order_status, order_number=order_number)
        except ValidationError:
            return JsonResponse({'status': 400, 'msg': '请输入有效日期'})
        return JsonResponse({'status': 200, 'msg': '编辑成功'})


# 买家导入
@login_required
def buyer_import(request):

    if request.method == "POST":
        import time
        buyers = 'buyers'
        date = time.strftime("%Y%m%d")
        time = time.strftime("%H%M%S") + '-'
        file = request.FILES.get('file')
        layout = file.name.split(".")[-1]
        if layout != "xlsx":
            return JsonResponse({"status": 400, "msg": "表格必须为xlsx格式"})
        if file:
            floder = os.path.join(EXCEL_PATH, buyers, date)
            if not os.path.isdir(floder):
                os.makedirs(floder, exist_ok=True)
            path_file = os.path.join(floder, time + file.name)
            with open(path_file, 'wb') as f:
                for line in file.chunks():
                    f.write(line)  # 保存到本地路径

            result = buyers_handler(path_file)  # 写入数据库
            if result == 'SUCCESS':
                return JsonResponse({'status': 200, 'msg': '导入成功'})
            else:
                return JsonResponse({'status': 400, 'msg': '数据获取失败，表格表头不一致'})
        return JsonResponse({'status': 400})


# 买家导出
@login_required
def buyer_export(request):
    content = request.GET.get('params')

    data = json.loads(content)

    search_first_order_time = False
    search_comment_last_time = False
    search_valid_order = False
    search_review_count = False
    search_cc_total = False
    search_review_percent = False
    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)

    platform = data.get('platform')
    site = data.get('site')
    buyer_status = data.get('buyer_status')
    cc = data.get('cc')
    order_vaild = data.get('order_vaild')
    member_type = data.get('member_type')
    review = data.get('review')
    comment_percent = data.get('comment_percent')
    buyer_number = data.get('buyer_number')
    buyer_phone = data.get('buyer_phone')
    buyer_email = data.get('buyer_email')
    member_expiry_time = data.get('member_expiry_time')
    order_first_time = data.get('order_first_time')
    comment_last_time = data.get('comment_last_time')

    kwargs = {}
    if platform:
        kwargs.update({
            'platform': platform
        })
    if site:
        kwargs.update({
            'buyer_site': site
        })
    if buyer_status:
        kwargs.update({
            'buyer_status': buyer_status
        })
    if member_type:
        kwargs.update({
            'member_type': member_type
        })
    if buyer_number:
        kwargs.update({
            'number': buyer_number
        })
    if buyer_phone:
        kwargs.update({
            'buyer_phone': buyer_phone
        })
    if platform:
        kwargs.update({
            'platform': platform
        })
    if buyer_email:
        kwargs.update({
            'buyer_email': buyer_email
        })
    if member_expiry_time:
        mx_start_time, mx_end_time = get_tilde_splitted_date_range(member_expiry_time)
        kwargs.update({
            'member_expiry_time__range': (mx_start_time, mx_end_time)
        })

    if order_first_time:
        start_time, end_time = get_tilde_splitted_date_range(order_first_time)
        search_first_order_time = True
    if comment_last_time:
        comment_last_time = str2date(comment_last_time)
        search_comment_last_time = True

    # Review数量（评论数量）
    if review:
        review = str2int(review)
        search_review_count = True
    # 累计CC金额权重
    if cc:
        cc = str2int(cc)
        search_cc_total = True
    # 累计有效订单
    if order_vaild:
        order_vaild = str2int(order_vaild)
        search_valid_order = True
    # 留评比
    if comment_percent:
        comment_percent = str2int(comment_percent)
        search_review_percent = True

    queryset_all = Buyer.objects.all().filter(**kwargs).order_by('-id')

    # ############ 筛选开始
    # 筛选首单时间
    if search_first_order_time is True:
        order_queryset = Order.objects.values('buyer__id'). \
            annotate(count=Count('buyer__id'), min=Min('create_time')). \
            filter(min__range=(start_time, end_time))
        ids = [obj['buyer__id'] for obj in order_queryset]
        queryset_all = queryset_all.filter(id__in=ids)

    # 筛选最后留评时间
    if search_comment_last_time is True:
        review_last = Order.objects.values('buyer__id'). \
            annotate(max=Max('review_time')). \
            filter(max=comment_last_time)
        ids = [obj['buyer__id'] for obj in review_last]
        queryset_all = queryset_all.filter(id__in=ids)

    # Review数量
    if search_review_count is True:
        review_count = Order.objects.values('buyer__id', 'review_type').filter(review_type='Review'). \
            annotate(count=Count('review_type')). \
            filter(count__gt=review)
        ids = [obj['buyer__id'] for obj in review_count]
        queryset_all = queryset_all.filter(id__in=ids)

    # 累计CC金额权重
    if search_cc_total is True:
        ids = []
        one_year_price = Order.objects.values('buyer__id').annotate(price_sum=Sum('purchase_price')). \
            filter(mode_payment='信用卡', create_time__gt=one_year_ago)
        for obj in one_year_price:
            if cc == 50 and int(obj['price_sum']) >= 50:
                ids.append(obj['buyer__id'])
            elif cc == 25 and 25 <= int(obj['price_sum']) < 50:
                ids.append(obj['buyer__id'])
            elif 0 < cc < 25 and 0 < int(obj['price_sum']) < 25:
                ids.append(obj['buyer__id'])
            elif cc == 0 and int(obj['price_sum']) == 0:
                ids.append(obj['buyer__id'])
        queryset_all = queryset_all.filter(id__in=ids)

    # 累计有效订单
    if search_valid_order is True:
        valid_order = Order.objects.values('buyer__id').filter(order_status="正常"). \
            annotate(count=Count('order_status')).filter(count__gt=order_vaild)
        ids = [obj['buyer__id'] for obj in valid_order]
        queryset_all = queryset_all.filter(id__in=ids)

    # 留评比 = Review数量/订单数量
    if search_review_percent is True:
        cursor = connection.cursor()
        sql = """
                    SELECT res.buyer_id, CONCAT(ROUND(SUM(res.pl_count)/SUM(res.order_count) * 100, 2), '', '%') as percent
                    FROM 
                    (
                        SELECT buyer_id,
                        CASE 
                            WHEN review_status != '未' THEN COUNT(id) ELSE 0 END AS pl_count, 
                        COUNT(id) AS order_count 
                        FROM customer_order
                        GROUP BY buyer_id, review_status
                    ) res
                    GROUP BY res.buyer_id having percent >= {}
                """.format(comment_percent)
        cursor.execute(sql)
        rows = cursor.fetchall()
        ids = [obj[0] for obj in rows]
        queryset_all = queryset_all.filter(id__in=ids)
    # ############ 筛选结束

    headers = ['序号', '买家编号', '买家状态', '会员类别', '会员过期时间', '注册手机', '注册邮箱',
               '12月累计信用卡金额', '累计有效订单金额', 'Review数量', '留评比', '首单时间', '最后评价时间']
    data_list = []
    index = 0
    for obj in queryset_all:
        index += 1
        # 会员过期时间
        member_expiry_time = obj.member_expiry_time.strftime("%m/%d/%Y") \
            if obj.member_expiry_time else ''

        # 12月信用卡累计金额
        one_year_price = Order.objects. \
            filter(mode_payment='信用卡', buyer_number=obj.number, create_time__gt=one_year_ago). \
            aggregate(sum_year=Sum('purchase_price'))
        one_year_price = one_year_price.get('sum_year') if one_year_price.get('sum_year') else '0'

        # 累计有效订单金额
        order_vaild_price = Order.objects.filter(buyer_number=obj.number, order_status='正常'). \
            aggregate(price=Sum('purchase_price'))
        order_vaild_price = order_vaild_price.get('price') if order_vaild_price else '0'

        # Review数量
        review_count = Order.objects.exclude(review_status='未').filter(buyer_number=obj.number).count()

        # 留评比 = Review数量/订单数量
        order_count = Order.objects.filter(buyer_number=obj.number).count()
        if int(review_count) == 0 or int(order_count) == 0:
            review_percent = '0'
        else:
            review_percent = '{:.2f}%'.format(int(review_count) / int(order_count) * 100)

        # 首单时间
        order_first = Order.objects.filter(buyer_number=obj.number).aggregate(min=Min('create_time'))
        order_first_time = order_first['min'].strftime("%m/%d/%Y") \
            if order_first['min'] else ''

        # 最后留评论时间
        review_last = Order.objects.filter(buyer_number=obj.number). \
            aggregate(max=Max('review_time'))
        review_last_time = review_last['max'].strftime("%m/%d/%Y") \
            if review_last['max'] else ''

        data_list.append([
            index,
            obj.number,
            obj.buyer_status,
            obj.member_type,
            member_expiry_time,
            obj.buyer_phone,
            obj.buyer_email,
            one_year_price,
            order_vaild_price,
            review_count,
            review_percent,
            order_first_time,
            review_last_time
        ])
    write = XlsxWriter('买家表')
    filename = write.set_header(headers).write(data_list).save_tmp()
    with open(filename, 'r') as output:
        file_name = '买家表.xlsx'

        response = StreamingHttpResponse(file_iterator(output.name))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Length'] = os.path.getsize(output.name)
        response['Content-Disposition'] = 'attachment; filename*="{0}"'.format(escape_uri_path(file_name))
        return response


# 订单导入
@login_required
def order_import(request):
    if request.method == "POST":
        import time
        orders = "orders"
        date = time.strftime("%Y%m%d")
        time = time.strftime("%H%M%S") + '-'
        file = request.FILES.get('file')
        layout = file.name.split(".")[-1]
        if layout != "xlsx":
            return JsonResponse({"status": 400, "msg": "表格必须为xlsx格式"})
        if file:
            floder = os.path.join(EXCEL_PATH, orders, date)
            if not os.path.isdir(floder):
                os.makedirs(floder, exist_ok=True)
            path_file = os.path.join(floder, time + file.name)
            print(path_file)
            with open(path_file, 'wb') as f:
                for line in file.chunks():
                    f.write(line)  # 保存到本地路径

            code = orders_handler(path_file)  # 写入数据库
            if code == 'SUCCESS':
                return JsonResponse({'status': 200, 'msg': '导入成功'})
            else:
                return JsonResponse({'status': 400, 'msg': '数据获取失败，表格表头不一致'})
        return JsonResponse({'status': 400})


# 订单导出
@login_required
def order_export(request):
    content = request.GET.get('params')
    data = json.loads(content)
    platform = data.get('platform')
    site = data.get('site')
    manager = data.get('manager')
    store_id = data.get('store_id')
    target_asin = data.get('target_asin')
    member_type = data.get('member_type')
    buyer_number = data.get('buyer_number')
    buyer_phone = data.get('buyer_phone')
    buyer_email = data.get('buyer_email')
    order_discount = data.get('order_discount')
    purchase_price = data.get('purchase_price')
    buyer_status = data.get('buyer_status')
    review_status = data.get('review_status')
    order_status = data.get('order_status')
    facebook_status = data.get('facebook_status')

    review_time = data.get('review_time')
    feedback_time = data.get('feedback_time')
    order_time = data.get('order_time')

    kwargs = {}
    if review_status:
        kwargs.update({
            'review_status': review_status
        })
    if order_status:
        kwargs.update({
            'order_status': order_status
        })
    if facebook_status:
        kwargs.update({
            'facebook_status': facebook_status
        })
    if order_discount:
        kwargs.update({
            'order_discount': order_discount
        })
    if purchase_price:
        kwargs.update({
            'purchase_price': purchase_price
        })
    if platform:
        kwargs.update({
            'platform': platform
        })
    if site:
        kwargs.update({
            'site': site
        })
    if buyer_number:
        kwargs.update({
            'buyer_number': buyer_number
        })
    if manager:
        kwargs.update({
            'manager': manager
        })
    if store_id:
        kwargs.update({
            'store_id': store_id
        })
    if target_asin:
        kwargs.update({
            'target_asin': target_asin
        })

    queryset = Order.objects.all().order_by('-id').order_by('-order_time')

    # 买家信息筛选
    if buyer_status:
        queryset = queryset.filter(buyer__buyer_status=buyer_status)
    if member_type:
        queryset = queryset.filter(buyer__member_type=member_type)
    if buyer_phone:
        queryset = queryset.filter(buyer__buyer_phone=buyer_phone)
    if buyer_email:
        queryset = queryset.filter(buyer__buyer_email=buyer_email)

    # 时间筛选
    if review_time:
        mx_start_time, mx_end_time = get_tilde_splitted_date_range(review_time)
        print('review_time:', mx_start_time, mx_end_time)
        queryset = queryset.filter(review_time__range=(mx_start_time, mx_end_time))
    if feedback_time:
        mx_start_time, mx_end_time = get_tilde_splitted_date_range(feedback_time)
        print('feedback_time:', mx_start_time, mx_end_time)
        queryset = queryset.filter(feedback_time__range=(mx_start_time, mx_end_time))
    if order_time:
        mx_start_time, mx_end_time = get_tilde_splitted_date_range(order_time)
        print('order_time:', mx_start_time, mx_end_time)
        queryset = queryset.filter(order_time__range=(mx_start_time, mx_end_time))

    queryset_all = queryset.filter(**kwargs)
    # ############ 筛选结束

    headers = ['序号', '买家编号', '平台', '站点', '操作员', '买家状态', '会员类别', '注册手机', '注册邮箱',
               '订单号', '目标ASIN', '店铺ID', '关联ASIN', '产品单价', '购买金额', '折扣off', 'Review状态',
               'Facebook状态', '订单时间', 'Review时间', 'FB时间']
    data_list = []
    index = 0
    for obj in queryset_all:
        index += 1

        buyer_obj = Buyer.objects.filter(number=obj.buyer_number).first()
        buyer_status = buyer_obj.buyer_status if buyer_obj else ''
        member_type = buyer_obj.member_type if buyer_obj else ''
        buyer_phone = buyer_obj.buyer_phone if buyer_obj else ''
        buyer_email = buyer_obj.buyer_email if buyer_obj else ''

        data_list.append([
            index,
            obj.buyer_number,
            obj.platform,
            obj.site,
            obj.manager,
            buyer_status,
            member_type,
            buyer_phone,
            buyer_email,
            obj.order_number,
            obj.target_asin,
            obj.store_id,
            obj.link_asin,
            obj.goods_price,
            obj.purchase_price,
            obj.order_discount,
            obj.review_status,
            obj.feedback_status,
            obj.order_time.strftime('%m/%d/%Y') if obj.order_time else '',
            obj.review_time.strftime('%m/%d/%Y') if obj.review_time else '',
            obj.feedback_time.strftime('%m/%d/%Y') if obj.feedback_time else '',
        ])

    write = XlsxWriter('订单表')
    filename = write.set_header(headers).write(data_list).save_tmp()
    with open(filename, 'r') as output:
        file_name = '订单表.xlsx'

        response = StreamingHttpResponse(file_iterator(output.name))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Length'] = os.path.getsize(output.name)
        response['Content-Disposition'] = 'attachment; filename*="{0}"'.format(escape_uri_path(file_name))
        return response
