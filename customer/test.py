import os
import datetime

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrderSystem.settings')

application = get_wsgi_application()

from django.db import connection
# starttime = datetime.datetime.now()
# sql = """
#         SELECT res.buyer_id, CONCAT(ROUND(SUM(res.pl_count)/SUM(res.order_count) * 100, 2), '', '%') as percent
#         FROM
#         (
#             SELECT buyer_id,
#             CASE
#                 WHEN review_status != '未' THEN COUNT(id) ELSE 0 END AS pl_count,
#             COUNT(id) AS order_count
#             FROM customer_order
#             GROUP BY buyer_id, review_status
#         ) res
#         GROUP BY res.buyer_id
#     """
#
# sql1 = """
#     SELECT buyer_id,
#             CASE
#                 WHEN review_status != '未' THEN COUNT(id) ELSE 0 END AS pl_count,
#             COUNT(id) AS order_count
#             FROM customer_order
#             GROUP BY buyer_id, review_status
# """
# cursor.execute(sql)
# rows = cursor.fetchall()
# for obj in rows:
#     print(obj)
# endtime = datetime.datetime.now()
#
# print((endtime - starttime).total_seconds())

# from customer.models import Buyer, Order
# from django.db.models import Max
#
# starttime = datetime.datetime.now()
# rows = Buyer.objects.all()
# for obj in rows:
#     print(obj.id, obj.buyer_status, obj.credit_card, obj.platform, obj.zip, obj.phones, obj.ip_name, obj.state, obj.order_finish_time)
# endtime  = datetime.datetime.now()
#
# print((endtime - starttime).total_seconds())

# starttime = datetime.datetime.now()
# review = Order.objects.order_by('-review_time')[0]
# endtime  = datetime.datetime.now()
# print((endtime - starttime).total_seconds())
#
# starttime = datetime.datetime.now()
# review = Order.objects.aggregate(max=Max('review_time'))
# endtime  = datetime.datetime.now()
# print((endtime - starttime).total_seconds())

# starttime = datetime.datetime.now()
# cursor = connection.cursor()
# sql = """
#         SELECT buyer_id, CASE WHEN review_type = 'Review'  THEN COUNT(*) ELSE 0 END AS review_count
#         FROM customer_order GROUP BY customer_order.buyer_id having review_count >= 0
#     """
# cursor.execute(sql)
# rows = cursor.fetchall()
# for obj in rows:
#     print("%s:%s" % (obj[0], obj[1]))
# endtime  = datetime.datetime.now()
# print((endtime - starttime).total_seconds())
#
#
# from django.db.models import Count
# starttime  = datetime.datetime.now()
# review_count = Order.objects.values('buyer__id', 'review_type').filter(review_type='Review').\
#             annotate(count=Count('review_type'))
# for obj in review_count:
#     print("%s:%s" % (obj['buyer__id'], obj['count']))
# endtime  = datetime.datetime.now()
# print((endtime - starttime).total_seconds())

if __name__ == '__main__':
    import re
    request_url = '/backend/admin/update/'
    a = re.match('/backend/admin/update/', request_url)
    print(a)
