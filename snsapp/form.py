from django.forms import ModelForm
from snsapp.models import Profile


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
        if nickName:
            self.fields['nickName'].widget.attrs['value'] = nickName
        if img:
            self.fields['img'].widget.attrs['value'] = img
    def update(self, profile):
        profile.nickName = self.cleaned_data['nickName']
        profile.img = self.cleaned_data['img']
        profile.save()