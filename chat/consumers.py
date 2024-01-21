import json
 
from channels.generic.websocket import AsyncWebsocketConsumer
from snsapp.models import Cost, Messages, User
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
 
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
 
        await self.accept()
 
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
 
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
 
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,  {
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'receiver': receiver
        }
        )
 

        # WebSocketに対応したメッセージの送信処理

    async def decrease_user_point(self, username):
        # データベースからユーザーを取得し、ポイントを減算する
        user = await database_sync_to_async(User.objects.get)(username=username)
        cost = await database_sync_to_async(Cost.objects.get)(label="send")

        user.point -= cost.point  # ポイントを1減らす
        await database_sync_to_async(user.save)()  # 変更を保存

    async def chat_message(self, event):
        message = event['message']
        sender_name = event['sender']
        receiver_name = event['receiver']
        try:
            
            await self.decrease_user_point(sender_name)
            # メッセージオブジェクトを作成し、保存します
            sender = await database_sync_to_async(User.objects.get)(username=sender_name)
            receiver = await database_sync_to_async(User.objects.get)(username=receiver_name)

            message_object = Messages(
                description=message,
                sender_name=sender,
                sender_id=sender.id,
                receiver_name=receiver,
                receiver_id=receiver.id,
            )
            print(message_object)
            await database_sync_to_async(message_object.save)()

            # WebSocketを通じてメッセージを送信
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender.username,  # senderはUserモデルのインスタンスと仮定
                'receiver': receiver.username  # receiverもUserモデルのインスタンスと仮定
            }))
        except User.DoesNotExist:
            # ユーザーが存在しない場合のエラーメッセージ
            await self.send(text_data=json.dumps({
                'error': 'User not found.'
            }))
        except Exception as e:
            # その他のエラーの場合
            await self.send(text_data=json.dumps({
                'error': f'An error occurred: {str(e)}'
            }))