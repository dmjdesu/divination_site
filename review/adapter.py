from allauth.account.adapter import DefaultAccountAdapter
from .models import *

class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        # Do not persist the user yet so we pass commit=False
        # (last argument)
        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)

        if not form.cleaned_data.get('userType'):
            user.userType = UserType(USERTYPE_DEFAULT) # デフォルトのユーザ種別を設定
        else:
            user.userType = form.cleaned_data.get('userType')

        # ユーザIDを取得するために一旦保存する
        user.save()

        if int(user.userType) == USERTYPE_SUPPLIER:
            # サプライヤーユーザ
            supplier = UserDetailSupplier()
            supplier.user_id = user.id
            supplier.save()
        else:
            # それ以外は一般ユーザ
            user.userType = UserType(USERTYPE_BUYER)
            buyer = UserDetailBuyer()
            buyer.user_id = user.id
            buyer.save()