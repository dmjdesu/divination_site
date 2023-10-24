from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
 
 
class Command(BaseCommand):
 
    def handle(self, *args, **options):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_lobby',
            {
                'type': 'chat_message',
                'message': "event_trigered_from_custom_command"
            }
        )
 