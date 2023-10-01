from django.contrib import admin
from django.urls import path
from django.conf import settings            # settings.pyの変数
from django.conf.urls.static import static  # メディア表示

# App_Folderからviews.pyで定義した関数呼出
from .views import (
    CreateCheckoutSessionView,
    ProductTopPageView,
    SuccessPageView,
    CancelPageView,
    stripe_webhook,
    )

urlpatterns = [
    path('admin/', admin.site.urls),                                                                               # 管理画面
    path("", ProductTopPageView.as_view(), name="product-top-page"),                                               # 商品トップ
    path("create-checkout-session/<pk>/", CreateCheckoutSessionView.as_view(), name="create-checkout-session"),    # 個別商品決済画面
    path("success/", SuccessPageView.as_view(), name="success"),                                                   # 決済成功時にリダイレクト先
    path("cancel/", CancelPageView.as_view(), name="cancel"),                                                      # 決済キャンセル時のリダイレクト先
    path("webhook/", stripe_webhook, name="webhook"),                                                              # 追加 Webhook
]

# メディア表示
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)