from django.contrib import admin
from .models import Post,Connection,User,Messages

# Register your models here.
admin.site.register(Post)
admin.site.register(Connection)
admin.site.register(User)
#以下を追加
class MessagesAdmin(admin.ModelAdmin):
    list_display=('pk','description','sender_name', 'receiver_name','time', 'seen', 'timestamp')


admin.site.register(Messages, MessagesAdmin)   #