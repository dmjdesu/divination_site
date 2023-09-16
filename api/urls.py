from django.urls import path, include
from api.views import *
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = router.urls

