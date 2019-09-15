from django.db import models


class Buyer(models.Model):
    number = models.CharField(max_length=64, verbose_name='编号')
    platform = models.CharField(max_length=32, verbose_name='平台')

    # 设备信息
    ip = models.CharField(max_length=64, verbose_name='IP')
    ip_name = models.CharField(max_length=64, verbose_name='IP买家名', null=True, blank=True)
    ip_password = models.CharField(max_length=64, verbose_name='IP密码', null=True, blank=True)

    # 买家信息
    buyer_site = models.CharField(max_length=32, verbose_name='站点')
    buyer_name = models.CharField(max_length=32, verbose_name='买家姓名')
    buyer_login_password = models.CharField(max_length=64, verbose_name='买家登录密码')
    buyer_phone = models.CharField(max_length=64, verbose_name='注册手机')
    buyer_email = models.EmailField(max_length=64, verbose_name='邮箱')
    buyer_email_password = models.CharField(max_length=64, verbose_name='邮箱密码', null=True, blank=True)

    # 家庭信息
    partner_name = models.CharField(max_length=32, verbose_name='配偶姓名', null=True, blank=True)
    partner_email = models.EmailField(max_length=64, verbose_name='配偶邮箱', null=True, blank=True)
    partner_email_password = models.CharField(max_length=64, verbose_name='配偶邮箱密码', null=True, blank=True)

    # 社交信息
    facebook = models.CharField(max_length=64, verbose_name='Facebook', null=True, blank=True)
    gmail = models.CharField(max_length=64, verbose_name='Gmail', null=True, blank=True)
    twitter = models.CharField(max_length=64, verbose_name='Twitter', null=True, blank=True)
    youtube = models.CharField(max_length=64, verbose_name='Youtube', null=True, blank=True)

    # 信用卡信息
    credit_card = models.CharField(max_length=64, verbose_name='信用卡卡号', null=True, blank=True)
    credit_card_expiry = models.DateTimeField(verbose_name='信用卡过期时间', null=True, blank=True)
    credit_card_cvv = models.CharField(max_length=64, verbose_name='CVV', null=True, blank=True)
    credit_card_origin = models.CharField(max_length=64, verbose_name='信用卡来源', null=True, blank=True)

    # 会员状态
    member_status = models.CharField(max_length=32, verbose_name='会员状态', null=True, blank=True)
    member_type = models.CharField(max_length=32, verbose_name='会员类别', null=True, blank=True)
    member_apply_time = models.DateTimeField(verbose_name='申请时间', null=True, blank=True)
    member_expiry_time = models.DateTimeField(verbose_name='过期时间', null=True, blank=True)

    # 收货地址
    first_name = models.CharField(max_length=32, verbose_name='名字', null=True, blank=True)
    last_name = models.CharField(max_length=32, verbose_name='姓', null=True, blank=True)
    address1 = models.CharField(max_length=64, verbose_name='收货地址', null=True, blank=True)
    city = models.CharField(max_length=64, verbose_name='城市', null=True, blank=True)
    state = models.CharField(max_length=64, verbose_name='州', null=True, blank=True)
    zip = models.CharField(max_length=64, verbose_name='zip', null=True, blank=True)
    phones = models.CharField(max_length=64, verbose_name='电话', null=True, blank=True)

    # 订单状态
    order_number = models.CharField(max_length=32, verbose_name='购买订单号', null=True, blank=True)
    order_payment = models.CharField(max_length=32, verbose_name='付款方式', null=True, blank=True)
    order_price = models.CharField(max_length=32, verbose_name='购买价格', null=True, blank=True)
    order_discount = models.CharField(max_length=32, verbose_name='购买折扣', null=True, blank=True)
    order_time = models.DateTimeField(verbose_name='订单时间', null=True, blank=True)
    order_finish_time = models.DateTimeField(verbose_name='订单完成时间', null=True, blank=True)
    order_task_type = models.CharField(max_length=32, verbose_name='订单任务类型', null=True, blank=True)
    order_comment = models.CharField(max_length=32, verbose_name='留评情况', null=True, blank=True)

    # 其他信息
    buyer_status = models.CharField(max_length=32, verbose_name='买家状态', null=True, blank=True)
    buyer_ua = models.CharField(max_length=64, verbose_name='UA', null=True, blank=True)
    buyer_cookie = models.CharField(max_length=64, verbose_name='Cookie', null=True, blank=True)

    # search
    first_order_time = models.DateTimeField(verbose_name="首单时间", null=True, blank=True)

    def __str__(self):
        return self.number


class Order(models.Model):
    buyer = models.ForeignKey(to="Buyer", verbose_name='买家', on_delete=models.CASCADE, null=True, blank=True)

    buyer_number = models.CharField(max_length=64, verbose_name='买家编号')

    manager = models.CharField(max_length=32, verbose_name='操作员')

    platform = models.CharField(max_length=32, verbose_name='平台')
    register_email = models.CharField(max_length=64, verbose_name='注册邮箱')
    task_type = models.CharField(max_length=32, verbose_name='任务类型')
    interface_type = models.CharField(max_length=32, verbose_name='入口类型')

    # 公用属性
    site = models.CharField(max_length=32, verbose_name='站点')
    select_key = models.CharField(max_length=64, verbose_name='搜索关键字', null=True, blank=True)
    target_asin = models.CharField(max_length=64, verbose_name='目标ASIN', null=True, blank=True)
    link_asin = models.CharField(max_length=64, verbose_name='关联ASIN', null=True, blank=True)
    target_goods_title = models.CharField(max_length=64, verbose_name='目标商品标题')
    store_id = models.CharField(max_length=64, verbose_name='店铺ID')

    # 购买purchase
    goods_price = models.CharField(max_length=64, verbose_name='商品单价')
    purchase_quantity = models.CharField(max_length=64, verbose_name='购买数量')
    purchase_price = models.CharField(max_length=64, verbose_name='购买金额')
    discount_code = models.CharField(max_length=64, verbose_name='折扣码', null=True, blank=True)
    order_discount = models.CharField(max_length=32, verbose_name='折扣off', null=True, blank=True)
    mode_payment = models.CharField(max_length=64, verbose_name='支付方式')
    deliver_type = models.CharField(max_length=32, verbose_name='发货类型')
    share_type = models.CharField(max_length=32, verbose_name='分享链接', null=True, blank=True)

    # 信用卡
    card_number = models.CharField(max_length=64, verbose_name='信用卡号', null=True, blank=True)
    card_expired_time = models.DateTimeField(max_length=32, verbose_name='过期时间', null=True, blank=True)
    card_cvv = models.CharField(max_length=64, verbose_name='cvv', null=True, blank=True)

    # 收货地址
    first_name = models.CharField(max_length=32, verbose_name='名字', null=True, blank=True)
    last_name = models.CharField(max_length=32, verbose_name='姓', null=True, blank=True)
    address1 = models.CharField(max_length=64, verbose_name='收货地址', null=True, blank=True)
    city = models.CharField(max_length=64, verbose_name='城市', null=True, blank=True)
    state = models.CharField(max_length=32, verbose_name='州', null=True, blank=True)
    zip = models.CharField(max_length=64, verbose_name='zip', null=True, blank=True)
    phones = models.CharField(max_length=64, verbose_name='电话', null=True, blank=True)

    # 留评
    review_type = models.CharField(max_length=64, verbose_name='留评类型', null=True, blank=True)
    review_title = models.CharField(max_length=64, verbose_name='留评标题', null=True, blank=True)
    review_content = models.CharField(max_length=64, verbose_name='留评内容', null=True, blank=True)
    review_status = models.CharField(max_length=64, verbose_name='留评状态', null=True, blank=True)
    review_time = models.DateTimeField(max_length=64, verbose_name='留评时间', null=True, blank=True)

    # 信息录入
    handle_status = models.CharField(max_length=64, verbose_name='操作状态', null=True, blank=True)
    order_status = models.CharField(max_length=64, verbose_name='订单状态', null=True, blank=True)
    order_number = models.CharField(max_length=64, verbose_name='订单号', null=True, blank=True)

    create_time = models.DateTimeField(max_length=32, verbose_name='录入时间', null=True, blank=True)
    order_time = models.DateTimeField(verbose_name='订单时间', null=True, blank=True)
    finish_time = models.DateTimeField(max_length=32, verbose_name='完成时间', null=True, blank=True)

    feedback_title = models.CharField(max_length=32, verbose_name='Feedback标题', null=True, blank=True)
    feedback_time = models.DateTimeField(max_length=32, verbose_name='Feedback时间', null=True, blank=True)
    feedback_status = models.CharField(max_length=32, verbose_name='Feedback状态', null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.buyer_number, self.order_number)
