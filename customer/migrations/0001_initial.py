# Generated by Django 2.1.4 on 2019-09-06 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=64, verbose_name='编号')),
                ('platform', models.CharField(max_length=32, verbose_name='平台')),
                ('ip', models.CharField(max_length=64, verbose_name='IP')),
                ('ip_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='IP买家名')),
                ('ip_password', models.CharField(blank=True, max_length=64, null=True, verbose_name='IP密码')),
                ('buyer_site', models.CharField(max_length=32, verbose_name='站点')),
                ('buyer_name', models.CharField(max_length=32, verbose_name='买家姓名')),
                ('buyer_login_password', models.CharField(max_length=64, verbose_name='买家登录密码')),
                ('buyer_phone', models.CharField(max_length=64, verbose_name='注册手机')),
                ('buyer_email', models.EmailField(max_length=64, verbose_name='邮箱')),
                ('buyer_email_password', models.CharField(blank=True, max_length=64, null=True, verbose_name='邮箱密码')),
                ('partner_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='配偶姓名')),
                ('partner_email', models.EmailField(blank=True, max_length=64, null=True, verbose_name='配偶邮箱')),
                ('partner_email_password', models.CharField(blank=True, max_length=64, null=True, verbose_name='配偶邮箱密码')),
                ('facebook', models.CharField(blank=True, max_length=64, null=True, verbose_name='Facebook')),
                ('gmail', models.CharField(blank=True, max_length=64, null=True, verbose_name='Gmail')),
                ('twitter', models.CharField(blank=True, max_length=64, null=True, verbose_name='Twitter')),
                ('youtube', models.CharField(blank=True, max_length=64, null=True, verbose_name='Youtube')),
                ('credit_card', models.CharField(blank=True, max_length=64, null=True, verbose_name='信用卡卡号')),
                ('credit_card_expiry', models.DateTimeField(blank=True, null=True, verbose_name='信用卡过期时间')),
                ('credit_card_cvv', models.CharField(blank=True, max_length=64, null=True, verbose_name='CVV')),
                ('credit_card_origin', models.CharField(blank=True, max_length=64, null=True, verbose_name='信用卡来源')),
                ('member_status', models.CharField(blank=True, max_length=32, null=True, verbose_name='会员状态')),
                ('member_type', models.CharField(blank=True, max_length=32, null=True, verbose_name='会员类别')),
                ('member_apply_time', models.DateTimeField(blank=True, null=True, verbose_name='申请时间')),
                ('member_expiry_time', models.DateTimeField(blank=True, null=True, verbose_name='过期时间')),
                ('first_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='名字')),
                ('last_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='姓')),
                ('address1', models.CharField(blank=True, max_length=64, null=True, verbose_name='收货地址')),
                ('city', models.CharField(blank=True, max_length=64, null=True, verbose_name='城市')),
                ('state', models.CharField(blank=True, max_length=64, null=True, verbose_name='州')),
                ('zip', models.CharField(blank=True, max_length=64, null=True, verbose_name='zip')),
                ('phones', models.CharField(blank=True, max_length=64, null=True, verbose_name='电话')),
                ('order_number', models.CharField(blank=True, max_length=32, null=True, verbose_name='购买订单号')),
                ('order_payment', models.CharField(blank=True, max_length=32, null=True, verbose_name='付款方式')),
                ('order_price', models.CharField(blank=True, max_length=32, null=True, verbose_name='购买价格')),
                ('order_discount', models.CharField(blank=True, max_length=32, null=True, verbose_name='购买折扣')),
                ('order_time', models.DateTimeField(blank=True, null=True, verbose_name='订单时间')),
                ('order_finish_time', models.DateTimeField(blank=True, null=True, verbose_name='订单完成时间')),
                ('order_task_type', models.CharField(blank=True, max_length=32, null=True, verbose_name='订单任务类型')),
                ('order_comment', models.CharField(blank=True, max_length=32, null=True, verbose_name='留评情况')),
                ('buyer_status', models.CharField(blank=True, max_length=32, null=True, verbose_name='买家状态')),
                ('buyer_ua', models.CharField(blank=True, max_length=64, null=True, verbose_name='UA')),
                ('buyer_cookie', models.CharField(blank=True, max_length=64, null=True, verbose_name='Cookie')),
                ('first_order_time', models.DateTimeField(blank=True, null=True, verbose_name='首单时间')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_number', models.CharField(max_length=64, verbose_name='买家编号')),
                ('manager', models.CharField(max_length=32, verbose_name='操作员')),
                ('platform', models.CharField(max_length=32, verbose_name='平台')),
                ('register_email', models.CharField(max_length=64, verbose_name='注册邮箱')),
                ('task_type', models.CharField(max_length=32, verbose_name='任务类型')),
                ('interface_type', models.CharField(max_length=32, verbose_name='入口类型')),
                ('site', models.CharField(max_length=32, verbose_name='站点')),
                ('select_key', models.CharField(blank=True, max_length=64, null=True, verbose_name='搜索关键字')),
                ('target_asin', models.CharField(blank=True, max_length=64, null=True, verbose_name='目标ASIN')),
                ('link_asin', models.CharField(blank=True, max_length=64, null=True, verbose_name='关联ASIN')),
                ('target_goods_title', models.CharField(max_length=64, verbose_name='目标商品标题')),
                ('store_id', models.CharField(max_length=64, verbose_name='店铺ID')),
                ('goods_price', models.CharField(max_length=64, verbose_name='商品单价')),
                ('purchase_quantity', models.CharField(max_length=64, verbose_name='购买数量')),
                ('purchase_price', models.CharField(max_length=64, verbose_name='购买金额')),
                ('discount_code', models.CharField(blank=True, max_length=64, null=True, verbose_name='折扣码')),
                ('order_discount', models.CharField(blank=True, max_length=32, null=True, verbose_name='折扣off')),
                ('mode_payment', models.CharField(max_length=64, verbose_name='支付方式')),
                ('deliver_type', models.CharField(max_length=32, verbose_name='发货类型')),
                ('share_type', models.CharField(blank=True, max_length=32, null=True, verbose_name='分享链接')),
                ('card_number', models.CharField(blank=True, max_length=64, null=True, verbose_name='信用卡号')),
                ('card_expired_time', models.DateTimeField(blank=True, max_length=32, null=True, verbose_name='过期时间')),
                ('card_cvv', models.CharField(blank=True, max_length=64, null=True, verbose_name='cvv')),
                ('first_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='名字')),
                ('last_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='姓')),
                ('address1', models.CharField(blank=True, max_length=64, null=True, verbose_name='收货地址')),
                ('city', models.CharField(blank=True, max_length=64, null=True, verbose_name='城市')),
                ('state', models.CharField(blank=True, max_length=32, null=True, verbose_name='州')),
                ('zip', models.CharField(blank=True, max_length=64, null=True, verbose_name='zip')),
                ('phones', models.CharField(blank=True, max_length=64, null=True, verbose_name='电话')),
                ('review_type', models.CharField(blank=True, max_length=64, null=True, verbose_name='留评类型')),
                ('review_title', models.CharField(blank=True, max_length=64, null=True, verbose_name='留评标题')),
                ('review_content', models.CharField(blank=True, max_length=64, null=True, verbose_name='留评内容')),
                ('review_status', models.CharField(blank=True, max_length=64, null=True, verbose_name='留评状态')),
                ('review_time', models.DateTimeField(blank=True, max_length=64, null=True, verbose_name='留评时间')),
                ('handle_status', models.CharField(blank=True, max_length=64, null=True, verbose_name='操作状态')),
                ('order_status', models.CharField(blank=True, max_length=64, null=True, verbose_name='订单状态')),
                ('order_number', models.CharField(blank=True, max_length=64, null=True, verbose_name='订单号')),
                ('create_time', models.DateTimeField(max_length=32, verbose_name='录入时间')),
                ('finish_time', models.DateTimeField(blank=True, max_length=32, null=True, verbose_name='完成时间')),
                ('feedback_title', models.CharField(blank=True, max_length=32, null=True, verbose_name='Feedback标题')),
                ('feedback_time', models.DateTimeField(blank=True, max_length=32, null=True, verbose_name='Feedback时间')),
                ('feedback_status', models.CharField(blank=True, max_length=32, null=True, verbose_name='Feedback状态')),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.Buyer', verbose_name='买家')),
            ],
        ),
    ]