import os
import django
from backend.utils import str2date
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OrderSystem.settings")        # 项目名称.settings
django.setup()

from customer.models import Buyer, Order


# 导入买家xlsx
def buyers_handler(local_path):

    data_pass = True

    df = pd.read_excel(local_path)
    df = df.fillna('')             # 由于pandas读取到为空的值会显示为nan，所有替换成空字符串

    buyers_list = []

    for i in df.index.values:               # 获取行号的索引，并对其进行遍历：
        try:
            # 根据i来获取每一行指定的数据 并利用to_dict转成字典 df.ix[0] 表示第一行

            row_data = df.loc[i, ['所在买家编号', 'IP', 'IP买家名', 'IP密码', '平台', '站点', '买家姓名', '注册手机',
                                 '注册邮箱',	'买家登录密码', '邮箱密码', '配偶姓名', '配偶邮箱',	'配偶邮箱密码', 'Facebook',
                                 'Gmail', 'Twitter', 'Youtube', '信用卡_卡号', '信用卡_过期时间', 'CVV', '会员申请时间',
                                 '会员类别', '会员过期时间', 'First Name', 'Last Name', 'Address1', 'City', 'State',
                                 'Zip', 'phones', '购买订单号', '付款方式', '购买价格', '购买折扣', '订单时间', '留评情况',
                                 '买家状态', 'UA', 'Cookie']].to_dict()
        except KeyError as e:
            # print('error: ', e)
            return 'FAIL'
        else:
            number = row_data.get('所在买家编号')
            # print(number)
            if Buyer.objects.filter(number=number).exists():
                continue

            credit_card_expiry = str2date(row_data.get('信用卡_过期时间')) \
                if row_data.get('信用卡_过期时间') else None

            member_apply_time = str2date(row_data.get('会员申请时间')) \
                if row_data.get('会员申请时间') else None

            member_expiry_time = str2date(row_data.get('会员过期时间')) \
                if row_data.get('会员过期时间') else None

            order_time = str2date(row_data.get('订单时间'))\
                if row_data.get('订单时间') else None

            order_finish_time = str2date(row_data.get('订单完成时间')) \
                if row_data.get('订单完成时间') else None

            if isinstance(member_expiry_time, str):
                data_pass = False

            if isinstance(order_finish_time, str):
                data_pass = False

            if isinstance(credit_card_expiry, str):
                data_pass = False

            if isinstance(order_time, str):
                data_pass = False

            if isinstance(member_apply_time, str):
                data_pass = False

            if data_pass:
                buyers_list.append(Buyer(
                    number=row_data.get('所在买家编号'),
                    platform=row_data.get('平台'),
                    ip=row_data.get('IP'),
                    ip_name=row_data.get('IP买家名'),
                    ip_password=row_data.get('IP密码'),
                    buyer_site=row_data.get('站点'),
                    buyer_name=row_data.get('买家姓名'),
                    buyer_login_password=row_data.get('买家登录密码'),
                    buyer_phone=row_data.get('注册手机'),
                    buyer_email=row_data.get('注册邮箱'),
                    buyer_email_password=row_data.get('邮箱密码'),
                    partner_name=row_data.get('配偶姓名'),
                    partner_email=row_data.get('配偶邮箱'),
                    partner_email_password=row_data.get('配偶邮箱密码'),
                    facebook=row_data.get('Facebook'),
                    gmail=row_data.get('Gmail'),
                    twitter=row_data.get('Twitter'),
                    youtube=row_data.get('Youtube'),
                    credit_card=row_data.get('信用卡_卡号'),
                    credit_card_expiry=credit_card_expiry,
                    credit_card_cvv=row_data.get('CVV'),
                    credit_card_origin=row_data.get('信用卡来源'),
                    member_status=row_data.get('会员状态'),
                    member_type=row_data.get('会员类别'),
                    member_apply_time=member_apply_time,
                    member_expiry_time=member_expiry_time,
                    first_name=row_data.get('First Name'),
                    last_name=row_data.get('Last Name'),
                    address1=row_data.get('Address1'),
                    city=row_data.get('City'),
                    state=row_data.get('State'),
                    zip=row_data.get('Zip'),
                    phones=row_data.get('phones'),
                    order_number=row_data.get('购买订单号'),
                    order_payment=row_data.get('付款方式'),
                    order_price=row_data.get('购买价格'),
                    order_discount=row_data.get('购买折扣'),
                    order_time=order_time,
                    order_finish_time=order_finish_time,
                    order_task_type=row_data.get('订单任务类型'),
                    order_comment=row_data.get('留评情况'),
                    buyer_status=row_data.get('买家状态'),
                    buyer_ua=row_data.get('UA'),
                    buyer_cookie=row_data.get('Cookie'),
                ))

    Buyer.objects.bulk_create(buyers_list)
    # print(buyers_list)

    return 'SUCCESS'


# 导入订单xlsx
def orders_handler(local_path):

    df = pd.read_excel(local_path)
    df = df.fillna('')             # 由于pandas读取到为空的值会显示为nan，所有替换成空字符串

    orders_list = []

    for i in df.index.values:               # 获取行号的索引，并对其进行遍历：
        try:
            # 根据i来获取每一行指定的数据 并利用to_dict转成字典 df.ix[0] 表示第一行

            row_data = df.loc[i, ['买家编号', '操作员', '平台', '注册邮箱', '任务类型', '入口类型', '站点',
                                  '搜索关键字', '目标ASIN', '目标商品标题', '店铺ID', '商品单价', '购买数量',
                                  '折扣码', '购买金额',	 '支付方式', '发货类型', '分享链接',
                                  'card number', 'Expired Date', 'CVV', 'First Name', 'Last Name',
                                  'Address1', 'City', 'State', 'Zip', 'phones', '类型', '标题', '内容',
                                  '操作状态', '留评状态', '订单号', '订单状态', '录入时间']].to_dict()
        except KeyError as e:
            # print('error: ', e)
            return 'FAIL'
        else:
            number = row_data.get('订单号')
            # print(number)
            if Order.objects.filter(order_number=number).exists():
                Order.objects.filter(order_number=number).delete()

            card_expired_time = str2date(row_data.get('Expired Date')) \
                if row_data.get('Expired Date') else None

            create_time = str2date(row_data.get('录入时间'))\
                if row_data.get('录入时间') else None

            if isinstance(create_time, str):
                continue

            if isinstance(card_expired_time, str):
                continue

            buyer_number = row_data.get('买家编号')
            buyer = Buyer.objects.filter(number=buyer_number).first()
            orders_list.append(Order(
                buyer_number=buyer_number,
                manager=row_data.get('操作员'),
                platform=row_data.get('平台'),

                register_email=row_data.get('注册邮箱'),
                task_type=row_data.get('任务类型'),
                interface_type=row_data.get('入口类型'),

                site=row_data.get('站点'),
                select_key=row_data.get('搜索关键字'),
                target_asin=row_data.get('目标ASIN'),
                target_goods_title=row_data.get('目标商品标题'),
                store_id=row_data.get('店铺ID'),

                goods_price=row_data.get('商品单价'),
                purchase_quantity=row_data.get('购买数量'),
                discount_code=row_data.get('折扣码'),
                purchase_price=row_data.get('购买金额'),
                mode_payment=row_data.get('支付方式'),
                deliver_type=row_data.get('发货类型'),
                share_type=row_data.get('分享链接'),

                card_number=row_data.get('card number'),
                card_cvv=row_data.get('CVV'),

                first_name=row_data.get('First Name'),
                last_name=row_data.get('Last Name'),
                address1=row_data.get('Address1'),
                city=row_data.get('City'),
                state=row_data.get('State'),
                zip=row_data.get('Zip'),
                phones=row_data.get('phones'),

                review_type=row_data.get('类型'),
                review_title=row_data.get('标题'),
                review_content=row_data.get('内容'),
                handle_status=row_data.get('操作状态'),
                review_status=row_data.get('留评状态'),

                order_number=row_data.get('订单号'),
                order_status=row_data.get('订单状态'),

                card_expired_time=card_expired_time,
                create_time=create_time,

                buyer=buyer
            ))

    Order.objects.bulk_create(orders_list)
    # print(buyers_list)

    return 'SUCCESS'


if __name__ == '__main__':
    res = buyers_handler('C:\\tempalte.xlsx')
    print(res)
