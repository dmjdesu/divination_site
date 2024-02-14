from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from config import settings

SHOP_LABEL = (
    ("send", 'send mesasge'),
    ("divination", 'send divination'),
)

class Cost(models.Model):
    label = models.CharField(max_length=30, choices=SHOP_LABEL)
    point = models.PositiveIntegerField(default=0)

def upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['images', str(instance.userPro.id)+str(instance.nickName)+str(".")+str(ext)])

class Connection(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='connections' , on_delete=models.CASCADE)
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='following', blank=True)

    def __str__(self):
        return self.user.username
    
    def follow(self, user_to_follow):
        if user_to_follow != self.user:  # ユーザーが自分自身をフォローしないようにする
            self.following.add(user_to_follow)
            self.save()

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('email is must')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

DIVINER_TYPE_CHOICES = (
        (11, '命術_四柱推命'),
        (12, '命術_紫微斗数'),
        (13, '命術_風水'),
        (21, '卜術_易経'),
        (22, '卜術_タロット'),
        (23, '卜術_ルーン'),
        (24, '卜術_オーラ'),
        (25, '卜術_ペンデュラム'),
        (31, '相術_手相'),
        (32, '相術_顔相'),
        (33, '相術_人相'),
        (34, '相術_波動'),
        (41, '霊感_オラクルカード'),
        (42, '霊感_クレアボヤント'),
        (43, '霊感_透視'),
        (44, '霊感_オーラリーディング'),
        (51, '心理_心理学'),
        (52, '心理_占星術'),
        (53, '心理_動物占い'),
        (61, '数秘術'),
        (71, 'ドリームリーディング'),
    )

class DivinerType(models.Model):
    name = models.CharField(max_length=30, choices=DIVINER_TYPE_CHOICES)
class Config(models.Model):
    SETTING_CHOICES = [
        ('account_settings', 'アカウント・メルマガ設定'),
        ('help', 'ヘルプ'),
        ('account_deletion', '退会・アカウント削除'),
        ('pricing_system', '料金システム'),
        ('user_manual', 'ユーザーマニュアル'),
        ('terms_of_service', '利用規約'),
        ('privacy_policy', 'プライバシーポリシー'),
        ('spec_com_trans_law', '特定商取引法に基づく表示'),
        ('pricing_about', '料金について'),  # 新しく追加されたキー
        ('asset_settlement_law', '資産決済法に基づく表示'),  # 新しく追加されたキー
        ('about_carecan', 'ケアカンとは？'),  # 新しく追加されたキー
        ('features_of_carecan', 'ケアカンの特徴'),  # 新しく追加されたキー
    ]

    key = models.CharField(max_length=50, choices=SETTING_CHOICES, unique=True, primary_key=True)
    value = models.TextField() 

    def __str__(self):
        return self.get_key_display()

class User(AbstractBaseUser, PermissionsMixin):
    
    USER_TYPE_CHOICES = (
        ('占い師', '占い師'),
        ('顧客', '顧客'),
    )

    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    username = models.CharField(max_length=100, verbose_name="ユーザー名")
    usertype = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    divinertype = models.ManyToManyField(DivinerType, blank=True, null=True)
    # ポイント
    points = models.PositiveIntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] 

    def __str__(self):
        return self.username
    
    @property
    def divinertype_display(self):
        # divinertypeの各インスタンスの__str__メソッドを呼び出し、
        # 結果をカンマで区切って連結します。
        return ", ".join(str(divinertype.name) for divinertype in self.divinertype.all())
    
    @property
    def profile_data(self):
        try:
            # print(self.__dict__)
            # profile = self.profile
            profile = Profile.objects.get(userPro=self)
            return {
                'nickName': profile.nickName,
                'created_on': profile.created_on,
                'img': profile.img.url if profile.img else None,  # imgフィールドが空の場合を考慮
                'introduction':  profile.introduction,  # 自己紹介フィールドを追加
            }
        except:
            return None  # もしくは {} など、関連するProfileが存在しない場合の返り値を定義

class Profile(models.Model):
    nickName = models.CharField(max_length=20)
    userPro = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_path)
    receive_newsletter = models.BooleanField(default=False)  # メールマガジン受信フラグ
    introduction = models.TextField(blank=True, null=True)  # 自己紹介

    def __str__(self):
        return self.nickName
    
class Messages(models.Model):
    
    description = models.TextField()
    sender_name = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="送信者", on_delete=models.CASCADE, related_name='sender')
    sender_id = models.IntegerField(default=0)
    receiver_name = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="受信者", on_delete=models.CASCADE, related_name='receiver')
    receiver_id = models.IntegerField(default=0)
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'メッセージリスト'
        verbose_name_plural = 'メッセージリスト'