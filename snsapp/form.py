from django.forms import ModelForm
from snsapp.models import *
from django import forms
from django.forms.widgets import Select

from snsapp.widgets import MySelect2MultipleWidget
from .models import User  # User モデルをインポートする
from allauth.account.forms import SignupForm

class FoodChoices(models.TextChoices):
    BREAD = '占い師', '占い師'
    RICE = '顧客', '顧客'



class CustomSelect(Select):
    def __init__(self, *args, label_id=None, **kwargs):
        self.label_id = label_id
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.label_id:
            context['label_id'] = self.label_id
        return context

class SendMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)

class CustomSignupForm(SignupForm):  # SignupFormを継承する
    usertype = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,  # FoodChoicesから適切な選択肢に変更
        required=True,
        label='ユーザータイプ',
    )
    
    divinertype = forms.MultipleChoiceField(  # MultipleChoiceFieldに変更
        choices=DIVINER_TYPE_CHOICES,
        required=False,
        label='占いの種類',
        widget=MySelect2MultipleWidget(attrs={  # Use the custom widget
            'class': 'form-control col-12',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usertype'].widget.attrs.update({
            'class': 'form-control col-12',
            'id': 'id_usertype',
            'onchange': "document.querySelector('label[for=id_divinertype]').style.display = (this.value === '占い師') ? 'block' : 'none';",
        })
        self.fields['divinertype'].widget.attrs.update({
            'class': 'form-control col-12',
            'id': 'id_divinertype',
            'style': 'display:none;',
        })
    
    def signup(self, request, user):
        user.usertype = self.cleaned_data['usertype']
        
        # usertypeが占い師の場合、divinertypeも保存
        print(self.cleaned_data['divinertype'])
        if user.usertype == '占い師':
            user.divinertype.set(self.cleaned_data['divinertype'])  # setメソッドを使用して複数選択された値を保存
            
        user.save()
        return user

class ProfileChangeForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nickName',
            'img',
            'receive_newsletter'
        ]

    def __init__(self, nickName=None,img=None,receive_newsletter=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        # 各フィールドのカスタムラベルを設定
        self.fields['nickName'].label = "ニックネーム"
        self.fields['img'].label = "画像"
        self.fields['receive_newsletter'].label = "メールマガジンを受信する"

        # ユーザーの更新前情報をフォームに挿入
        self.fields['nickName'].widget.attrs['class'] = 'form-control col-12'
        self.fields['img'].widget.attrs['class'] = 'form-control col-12'
        self.fields['receive_newsletter'].widget.attrs['class'] = 'form-control col-12'
        if nickName:
            self.fields['nickName'].widget.attrs['value'] = nickName
        if img:
            self.fields['img'].widget.attrs['value'] = img
        if receive_newsletter:
            self.fields['img'].widget.attrs['value'] = receive_newsletter
    def update(self, profile):
        profile.nickName = self.cleaned_data['nickName']
        profile.img = self.cleaned_data['img']
        profile.receive_newsletter = self.cleaned_data['receive_newsletter']
        profile.save()

class DivinerTypeForm(forms.ModelForm):
    class Meta:
        model = DivinerType
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = DIVINER_TYPE_CHOICES