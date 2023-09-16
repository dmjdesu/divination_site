from decimal import Decimal
from django.contrib import admin

from review.models import *

admin.site.register(CustomUser)
admin.site.register(UserDetailSupplier)
admin.site.register(UserDetailBuyer)

