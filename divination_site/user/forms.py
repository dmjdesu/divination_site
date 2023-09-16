from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # 追加

from .models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "account_id",
            "email",
            "first_name",
            "last_name",
            "birth_date",
        )

# ログインフォームを追加
class LoginFrom(AuthenticationForm):
    class Meta:
        model = CustomUser