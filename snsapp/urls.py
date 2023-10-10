from django.urls import path
from .views import *


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('mydiviner/', MyDiviner.as_view(), name='mydiviner'),
    path('diviner/<int:pk>/', DivinerDetail.as_view(), name='diviner_detail'),
    path("search/", SearchUser.as_view(), name="search_user"),
    path('follow-home/<int:pk>', FollowHome.as_view(), name='follow-home'),
    path('follow-detail/<int:pk>', FollowDetail.as_view(), name='follow-detail'),
    path('follow_diviner/<int:pk>/', follow_diviner, name='follow_diviner'),
    path("chat/<str:username>", Message.as_view(), name="get_message"),  
    path('api/messages', UpdateMessage.as_view()),
    path('change/', ProfileChangeView.as_view(), name="change"),
]