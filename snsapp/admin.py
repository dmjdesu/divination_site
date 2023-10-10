from django.contrib import admin
from .models import *
from shopping.models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display=('img','nickName')

class MessagesAdmin(admin.ModelAdmin):
    list_display=('pk','description','sender_name', 'receiver_name','time', 'seen', 'timestamp')

class PriceInlineAdmin(admin.TabularInline):
    model = Price
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    inlines = [PriceInlineAdmin]
    
admin.site.register(Transaction)
admin.site.register(Product, ProductAdmin)
admin.site.register(Price)
admin.site.register(Connection)
admin.site.register(User)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Messages, MessagesAdmin)   #