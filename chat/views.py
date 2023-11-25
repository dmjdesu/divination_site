from django.db.models import OuterRef, Subquery, Q, CharField
from django.db.models.functions import Coalesce
from django.db.models.expressions import Value, ExpressionWrapper
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
 
from snsapp.models import DIVINER_TYPE_CHOICES, Cost, Messages, Connection, Profile, User

def index(request):
    return render(request, "chat/index.html")

def getFriendsList(self):
        """
        指定したユーザの友達リストを取得
        :param: ユーザ名
        :return: ユーザ名の友達リスト
        """
        try:
             # request.userのConnectionオブジェクトを取得
            connection = self.request.user.connections

            # Connectionオブジェクトからfollowing属性を使ってフォローしているユーザのリストを取得
            following_users = connection.following.all()

            # 各following_userに対する最新のメッセージのタイムスタンプのサブクエリを作成
            latest_timestamp_subquery = Messages.objects.filter(
                Q(sender_name=OuterRef('pk'), receiver_name=self.request.user) |
                Q(sender_name=self.request.user, receiver_name=OuterRef('pk'))
            ).order_by('-timestamp').values('timestamp')[:1]

            # 各following_userに対する最新のメッセージのタイムスタンプのサブクエリを作成
            latest_message_subquery = Messages.objects.filter(
                Q(sender_name=OuterRef('pk'), receiver_name=self.request.user) |
                Q(sender_name=self.request.user, receiver_name=OuterRef('pk'))
            ).order_by('-timestamp').values('description')[:1]
            

            # DateTimeFieldを文字列に変換するためのExpressionWrapperを使用
            timestamp_as_str = ExpressionWrapper(
                Subquery(latest_timestamp_subquery),
                output_field=CharField()
            )

            # ExpressionWrapperを使用してoutput_fieldをTextFieldに指定
            message_as_textfield = ExpressionWrapper(
                Subquery(latest_message_subquery),
                output_field=CharField()
            )

            # サブクエリを使って、各following_userに最新のメッセージのタイムスタンプと内容をアノテーションとして追加
            # Coalesceを使って、latest_message_timestampとlatest_messageがnullの場合にそれぞれ「未送信」と空白文字列を設定
            following_users_with_latest_message = following_users.annotate(
                latest_message_timestamp=Coalesce(
                    timestamp_as_str,
                    Value('未送信')
                ),
                latest_message=Coalesce(
                    message_as_textfield,
                    Value('')
                ),
            )
            return following_users_with_latest_message
        except Exception as ex:
            print(ex)
            return []
 
class Message(LoginRequiredMixin, View):
    def get(self,request, username):
        """
        特定ユーザ間のチャット情報を取得する
        """
        print(username)
        friend = User.objects.get(username=username)
        current_user = request.user
        chat_messages = Messages.objects.filter(
            (Q(sender_name=current_user.id) & Q(receiver_name=friend.id)) |
            (Q(sender_name=friend.id) & Q(receiver_name=current_user.id))
        )
        # friends = getFriendsList(self)
        return render(request, "chat/room.html",
                        {'chat_messages': chat_messages,
                        # 'friends': friends,
                        'room_name': username, # ここでroomNameを指定している
                        'current_user_name': current_user.username, 
                        'friend_name': friend.username
                        })
