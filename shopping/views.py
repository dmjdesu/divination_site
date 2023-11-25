import json
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Product
from .models import Price
from .models import Transaction # 追加
import datetime   # 追加
from django.contrib.auth import get_user_model

# STRIPEのシークレットキー
stripe.api_key = settings.STRIPE_SECRET_KEY

# WEBHOOKのシークレットキー
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

# 決済成功画面
class SuccessPageView(TemplateView):
    template_name = 'shopping/success.html'

# 決済キャンセル画面
class CancelPageView(TemplateView):
    template_name = 'shopping/cancel.html'

class ProductTopPageView(ListView):
    # 商品マスタ
    model = Product
    # ページリンク
    template_name = "shopping/product-top.html"
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "product_list"


# 決済画面
class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        # 商品マスタ呼出
        product = Product.objects.get(id=self.kwargs["pk"])
        price   = Price.objects.get(product=product)

        # ドメイン
        YOUR_DOMAIN = "http://127.0.0.1:8000"

        user_id = request.user.id 

        # 決済用セッション
        checkout_session = stripe.checkout.Session.create(
            # 決済方法
            payment_method_types=['card'],
            # 決済詳細
            line_items=[
                {
                    'price': price.stripe_price_id,       # 価格IDを指定
                    'quantity': 1,                        # 数量
                },
            ],
            # POSTリクエスト時にメタデータ取得
            metadata = {
                        "product_id":product.id,
                        "user_id": user_id,
                       },
            mode='payment',                               # 決済手段（一括）
            success_url=YOUR_DOMAIN + '/shopping/success/',        # 決済成功時のリダイレクト先
            cancel_url=YOUR_DOMAIN + '/shopping/cancel/',          # 決済キャンセル時のリダイレクト先
        )
        return redirect(checkout_session.url)




# イベントハンドラ
@csrf_exempt
def stripe_webhook(request):

    # サーバーのイベントログからの出力ステートメント
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # 有効でないpayload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # 有効でない署名
        return HttpResponse(status=400)

    # checkout.session.completedイベント検知
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # ユーザー識別のためのIDを取得（Stripeのcustomerから取得または別の方法を使用）
        user_id = session.get("metadata", {}).get("user_id")

        User = get_user_model

        # ユーザーモデルの取得
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # ユーザーが存在しない場合の処理
            return HttpResponse(status=404)

        # 商品情報取得
        product_id = session["metadata"]["product_id"]
        product = Product.objects.get(id=product_id)

        print(product.point)
        print(user.points)
        # ユーザーのポイントを更新
        user.points += product.point
        user.save()


        # イベント情報取得
        customer_name  = session["customer_details"]["name"]     # 顧客名
        customer_email = session["customer_details"]["email"]    # 顧客メール
        product_id     = session["metadata"]["product_id"]       # 購入商品ID
        product        = Product.objects.get(id=product_id)      # 購入商品情報
        product_name   = product.name                            # 購入した商品名
        amount         = session["amount_total"]                 # 購入金額（手数料抜き）

        # DBに結果を保存
        SaveTransaction(product_name, customer_name, customer_email, amount)
        print(session["metadata"])


        # 決済完了後メール送信（Djangoのメール機能利用）
        send_mail(
            subject = '商品購入完了！',                                                                                     # 件名
            message = '{}様\n商品購入ありがとうございます。購入された商品URLはこちら{}'.format(customer_name,product.url),  # メール本文
            recipient_list = [customer_email],                                                                              # TO
            from_email = 'test@test.com'                                                                                    # FROM
        )
        # 結果確認
        print(session)

    return HttpResponse(status=200)


# 顧客の商品購入履歴を保存
def SaveTransaction(product_name, customer_name, customer_email, amount):
    # DB保存
    saveData = Transaction.objects.get_or_create(
                        product_name   =  product_name,
                        date           = datetime.datetime.now(),
                        customer_name  = customer_name,
                        email          = customer_email,
                        product_amount = amount
                        )
    return saveData