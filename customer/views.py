# import json
# from .models import Buyer, Order
# from .serializers import BuyerSerializer, OrderSerializer
# from .pagination import ListPagination
#
# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
#
#
# class BuyersListCreate(generics.ListAPIView):
#     queryset = Buyer.objects.all().order_by('-id')
#     serializer_class = BuyerSerializer
#     pagination_class = ListPagination
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     def get(self, request, *args, **kwargs):
#         condition = request.GET.get('condition')
#         if condition:
#             data = json.loads(condition)
#             platform = data.get('platform')
#             site = data.get('site')
#             buyer_status = data.get('buyer_status')
#             cc = data.get('cc')
#             order_vaild = data.get('order_vaild')
#             member_type = data.get('member_type')
#             review = data.get('review')
#             comment_percent = data.get('comment_percent')
#             buyer_number = data.get('buyer_number')
#             buyer_phone = data.get('buyer_phone')
#             buyer_email = data.get('buyer_email')
#             member_expiry_time = data.get('member_expiry_time')
#             order_first_time = data.get('order_first_time')
#             comment_last_time = data.get('comment_last_time')
#
#             kwargs = {}
#             if platform:
#                 kwargs.update({
#                     'platform': platform
#                 })
#             if site:
#                 kwargs.update({
#                     'buyer_site': site
#                 })
#             if buyer_status:
#                 kwargs.update({
#                     'buyer_status': buyer_status
#                 })
#             if member_type:
#                 kwargs.update({
#                     'member_type': member_type
#                 })
#             if buyer_number:
#                 kwargs.update({
#                     'number': buyer_number
#                 })
#             if buyer_phone:
#                 kwargs.update({
#                     'buyer_phone': buyer_phone
#                 })
#             if platform:
#                 kwargs.update({
#                     'platform': platform
#                 })
#             if buyer_email:
#                 kwargs.update({
#                     'buyer_email': buyer_email
#                 })
#
#             if member_expiry_time:
#                 print(member_expiry_time)
#             if order_first_time:
#                 print(order_first_time)
#             if comment_last_time:
#                 print(comment_last_time)
#
#             # 累计CC金额权重
#             if cc:
#                 # do something
#                 pass
#             # 留评比
#             if comment_percent:
#                 # do something
#                 pass
#             # Review数量（评论数量）
#             if review:
#                 # do something
#                 pass
#             # 累计有效订单
#             if order_vaild:
#                 # do something
#                 pass
#
#         queryset_all = self.get_queryset().filter(**kwargs)
#         queryset = self.paginate_queryset(queryset_all)
#
#         serializer = BuyerSerializer(queryset, many=True)
#         return Response({
#             'code': 0,
#             'count': queryset_all.count(),
#             'data': serializer.data
#         })
#
#
# class OrderListCreate(generics.ListAPIView):
#     queryset = Order.objects.all().order_by('-id')
#     serializer_class = OrderSerializer
#     pagination_class = ListPagination
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     def get(self, request, *args, **kwargs):
#         queryset_all = self.get_queryset()
#         queryset = self.paginate_queryset(queryset_all)
#         serializer = OrderSerializer(queryset, many=True)
#         return Response({
#             'code': 0,
#             'count': queryset_all.count(),
#             'data': serializer.data
#         })
