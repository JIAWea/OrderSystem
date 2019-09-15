# Generated by Django 2.1.4 on 2019-09-14 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='订单时间'),
        ),
        migrations.AlterField(
            model_name='order',
            name='create_time',
            field=models.DateTimeField(blank=True, max_length=32, null=True, verbose_name='录入时间'),
        ),
    ]