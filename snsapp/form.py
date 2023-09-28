from django.forms import ModelForm
from snsapp.models import Profile
from django import forms
from django.db import models
from allauth.account.forms import SignupForm

class FoodChoices(models.TextChoices):
    BREAD = '占い師', '占い師'
    RICE = '顧客', '顧客'

class CustomSignupForm(SignupForm): #SignupFormを継承する
    usertype = forms.fields.ChoiceField(
        choices=FoodChoices.choices,
        required=True,
        label='ユーザータイプ',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usertype'].widget.attrs['class'] = 'form-control col-12'
    
    def signup(self, request, user):
        user.usertype = self.cleaned_data['usertype']
        user.save()
        return user

class ProfileChangeForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nickName',
            'img',
        ]

    def __init__(self, nickName=None,img=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        # ユーザーの更新前情報をフォームに挿入
        self.fields['nickName'].widget.attrs['class'] = 'form-control col-12'
        self.fields['img'].widget.attrs['class'] = 'form-control col-12'
        if nickName:
            self.fields['nickName'].widget.attrs['value'] = nickName
        if img:
            self.fields['img'].widget.attrs['value'] = img
    def update(self, profile):
        profile.nickName = self.cleaned_data['nickName']
        profile.img = self.cleaned_data['img']
        profile.save()