from __future__ import barry_as_FLUFL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

class Category(models.Model):
    name = models.CharField('ユーザーカテゴリー', max_length=255)

    def __str__(self):
        return self.name

class UserType(models.Model):
    """ ユーザ種別 """
    typename = models.CharField(verbose_name='ユーザ種別',
                                max_length=150)

    def __str__(self):
        return f'{self.id} - {self.typename}'

USERTYPE_SUPPLIER = 1
USERTYPE_BUYER = 2
USERTYPE_DEFAULT = USERTYPE_BUYER

class CustomUserManager(UserManager):
    """ 拡張ユーザーモデル向けのマネージャー """

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):

    #作成したマネージャークラスを使用
    objects = CustomUserManager()

    # モデル内にユーザ種別を持つ
    userType = models.ForeignKey(UserType,
                                verbose_name='ユーザ種別',
                                null=True,
                                blank=True,
                                on_delete=models.PROTECT)
    
    def __str__(self):
        return self.username

class UserDetailSupplier(models.Model):
    user = models.OneToOneField(CustomUser,
                                unique=True,
                                db_index=True,
                                related_name='detail_supplier',
                                on_delete=models.CASCADE)
    # サプライヤーユーザ向けの項目
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        user = CustomUser.objects.get(pk=self.user_id)
        return f'{user.id} - {user.username} - {user.email} - {self.id} - {self.companyName}'
    
class UserDetailBuyer(models.Model):
    user = models.OneToOneField(CustomUser,
                                unique=True,
                                db_index=True,
                                related_name='detail_buyer',
                                on_delete=models.CASCADE)
    # バイヤーユーザ向けの項目
    nearestStation = models.CharField(
                                   max_length=100,
                                   null=True,
                                   blank=True,
                                )
    def __str__(self):
        user = CustomUser.objects.get(pk=self.user_id)
        return f'{user.id} - {user.username} - {user.email} - {self.id} - {self.nearestStation}'