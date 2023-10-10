from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from config import settings

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


class User(AbstractBaseUser, PermissionsMixin):
    
    USER_TYPE_CHOICES = (
        ('占い師', '占い師'),
        ('顧客', '顧客'),
    )

    DIVINER_TYPE_CHOICES = (
        ('命術_四柱推命', '命術_四柱推命'),
        ('命術_紫微斗数', '命術_紫微斗数'),
        ('命術_風水', '命術_風水'),
        ('卜術_易経', '卜術_易経'),
        ('卜術_タロット', '卜術_タロット'),
        ('卜術_ルーン', '卜術_ルーン'),
        ('卜術_オーラ', '卜術_オーラ'),
        ('卜術_ペンデュラム', '卜術_ペンデュラム'),
        ('相術_手相', '相術_手相'),
        ('相術_顔相', '相術_顔相'),
        ('相術_人相', '相術_人相'),
        ('相術_波動', '相術_波動'),
        ('霊感_オラクルカード', '霊感_オラクルカード'),
        ('霊感_クレアボヤント', '霊感_クレアボヤント'),
        ('霊感_透視', '霊感_透視'),
        ('霊感_オーラリーディング', '霊感_オーラリーディング'),
        ('心理_心理学', '心理_心理学'),
        ('心理_占星術', '心理_占星術'),
        ('心理_動物占い', '心理_動物占い'),
        ('数秘術', '数秘術'),
        ('ドリームリーディング', 'ドリームリーディング'),
        # その他にも様々な種類が考えられます
    )

    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    username = models.CharField(max_length=100, verbose_name="ユーザー名")
    usertype = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    divinertype  = models.CharField(max_length=30, choices=DIVINER_TYPE_CHOICES)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] 

    def __str__(self):
        return self.username

class Profile(models.Model):
    nickName = models.CharField(max_length=20)
    userPro = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='userPro',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_path)

    def __str__(self):
        return self.nickName
    
class Messages(models.Model):
    
    description = models.TextField()
    sender_name = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="送信者", on_delete=models.CASCADE, related_name='sender')
    receiver_name = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="受信者", on_delete=models.CASCADE, related_name='receiver')
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'メッセージリスト'
        verbose_name_plural = 'メッセージリスト'