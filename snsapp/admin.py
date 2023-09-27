from django.contrib import admin
from .models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display=('img','nickName')

class MessagesAdmin(admin.ModelAdmin):
    list_display=('pk','description','sender_name', 'receiver_name','time', 'seen', 'timestamp')


admin.site.register(Post)
admin.site.register(Connection)
admin.site.register(User)
admin.site.register(Profile,ProfileAdmin)
#以下を追加


admin.site.register(Messages, MessagesAdmin)   #