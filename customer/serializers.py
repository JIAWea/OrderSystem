# from rest_framework import serializers
# from .models import Buyer, Order
#
#
# class BuyerSerializer(serializers.ModelSerializer):
#     # member_apply_time = serializers.DateTimeField(format="%m/%d/%Y")
#     member_expiry_time = serializers.DateTimeField(format="%m/%d/%Y")
#     # credit_card_expiry = serializers.DateTimeField(format="%m/%d/%Y")
#     # order_time = serializers.DateTimeField(format="%m/%d/%Y")
#     # order_finish_time = serializers.DateTimeField(format="%m/%d/%Y")
#
#     class Meta:
#         model = Buyer
#         fields = ('buyer_status', 'member_status', 'member_expiry_time', 'buyer_phone', 'buyer_email')
#
#
# class OrderSerializer(serializers.ModelSerializer):
#     create_time = serializers.DateTimeField(format="%m/%d/%Y")
#     finish_time = serializers.DateTimeField(format="%m/%d/%Y")
#     feedback_time = serializers.DateTimeField(format="%m/%d/%Y")
#     card_expired_time = serializers.DateTimeField(format="%m/%d/%Y")
#
#     class Meta:
#         model = Order
#         fields = '__all__'
