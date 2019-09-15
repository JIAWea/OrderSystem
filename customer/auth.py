# from rest_framework import authentication
# from rest_framework import exceptions
# from backend.models import BackendUser
#
#
# class MyAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         # username = request.META.get('X_USERNAME')
#         # if not username:
#         #     return None
#         try:
#             user = BackendUser.objects.get(name='admin')
#             print(user)
#
#         except BackendUser.DoesNotExist:
#             raise exceptions.AuthenticationFailed('No such user')
#
#         return (user, None)
