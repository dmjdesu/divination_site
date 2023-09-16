from django.urls import path
from .views import *

app_name = "review"
urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('profile/', HomeView.as_view(), name='profile'),
]
