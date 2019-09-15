from django.db import models


from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class BackendUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not name:
            raise ValueError('Users must have an name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


# 自定制admin后台管理员
class BackendUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=64, verbose_name="用户名", unique=True)
    email = models.EmailField(
        verbose_name='邮件',
        max_length=255,
        blank=True,
        null=True
    )
    roles = models.ManyToManyField(verbose_name='角色', to="Role", blank=True)

    is_active = models.BooleanField(default=True)         # 决定是否可以登录后台
    is_staff = models.BooleanField(default=True)          # 决定是否可以登录后台

    objects = BackendUserManager()
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.name

    # @property
    # def token(self):
    #     return self._generate_jwt_token()

    # def _generate_jwt_token(self):
    #     import jwt
    #     import datetime
    #     from OrderSystem.settings import SECRET_KEY
    #     user_info = {
    #         'iat': datetime.datetime.utcnow(),
    #         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
    #         'username': self.name,
    #         'sub': self.pk,
    #         'admin': self.is_superuser,
    #     }
    #     token = jwt.encode(user_info, SECRET_KEY, algorithm='HS256')
    #
    #     return token.decode('utf-8')

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    class Meta:
        verbose_name_plural = "后台管理员"


class Permission(models.Model):
    """
    权限表
    """
    name = models.CharField(verbose_name='名称', max_length=32, unique=True)
    url = models.CharField(verbose_name='url', max_length=128)
    method = models.CharField(verbose_name='请求方法', max_length=32)
    menu = models.ForeignKey(to="Menu", verbose_name="关联菜单", null=True, blank=True, on_delete=models.CASCADE)
    parents = models.ForeignKey(to="Permission", verbose_name="是否菜单权限", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "权限表"


class Role(models.Model):
    """
    角色
    """
    name = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    description = models.CharField(verbose_name='备注', max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "角色表"


class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(max_length=32, unique=True)
    parent = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)

    class Meta:
        verbose_name_plural = "菜单表"
