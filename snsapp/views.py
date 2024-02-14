from django.db.models import OuterRef, Subquery, Q, CharField, TextField
from django.db.models.functions import Coalesce
from django.db.models.expressions import Value, ExpressionWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.generic.edit import ProcessFormView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from shopping.models import Product
from .models import Config  # Config モデルのインポート
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout


from snsapp.form import DivinerTypeForm, ProfileChangeForm, SendMessageForm
from .serializers import MessageSerializer, UserSerializer

from .models import DIVINER_TYPE_CHOICES, Cost, Messages, Connection, Profile, User

class Home(LoginRequiredMixin, ListView):
    """HOMEページで、自分以外のユーザー投稿をリスト表示"""
    model = User
    template_name = 'home.html'

    def get_config_value(self,key):
        try:
            config = Config.objects.get(key=key)
            return config.value
        except Config.DoesNotExist:
            return None

    def get_queryset(self):
        """リクエストユーザーのみ除外"""
        return User.objects.filter(usertype="占い師")
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #get_or_createにしないとサインアップ時オブジェクトがないためエラーになる
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)

        current_user = self.request.user
        context['chat_messages'] =  Messages.objects.filter(
                (Q(sender_name=current_user.id) | Q(receiver_name=current_user.id))
            )
        context["about_carecan"] = self.get_config_value('about_carecan')
        context["features_of_carecan"] = self.get_config_value('features_of_carecan')
        return context
    
    
class MyDiviner(LoginRequiredMixin,ListView):
    """占い師一覧を表示"""
    model = User
    template_name = 'diviner_list.html'

    def get_queryset(self):
        queryset = User.objects.filter(usertype="占い師")
        
        divinertype_id = self.request.GET.get('name')
        diviner_type_dict = dict((value,name ) for value, name in DIVINER_TYPE_CHOICES)
        if divinertype_id:
            try:
                # divinertypeフィールドに対する__nameルックアップを使用してフィルタリングします。
                queryset = queryset.filter(divinertype__name__icontains= diviner_type_dict.get(int(divinertype_id)))
            except ValueError:
                print("ValueError")
                # ValueErrorをキャッチし、エラーメッセージをログに記録するなどの処理を追加します。
                pass  
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DivinerTypeForm(self.request.GET or None)
        context["point"] = self.request.user.points
        return context



###############################################################
#フォロー処理
class FollowBase(LoginRequiredMixin, View):
    pass
    # """フォローのベース。リダイレクト先を以降で継承先で設定"""
    # def get(self, request, *args, **kwargs):
    #     pk = self.kwargs['pk']
    #     target_user = Post.objects.get(pk=pk).user

    #     my_connection = Connection.objects.get_or_create(user=self.request.user)

    #     if target_user in my_connection[0].following.all():
    #         obj = my_connection[0].following.remove(target_user)
    #     else:
    #         obj = my_connection[0].following.add(target_user)
    #     return obj

def deduct_points(user, action_label):
    try:
        # コストオブジェクトを取得
        print(action_label)
        cost = Cost.objects.get(label=action_label)
    except Cost.DoesNotExist:
        # コストオブジェクトが存在しない場合はエラーを処理
        return {"error": "ポイントの指定が間違っています。"}

    # ユーザーのポイントが十分であることを確認
    print(user.username)
    print("user.username")
    if user.points < cost.point:
        return {"error": "ポイントが足りません。"}

    # ユーザーのポイントを減算
    user.points -= cost.point
    user.save()

    return {"success": f"{cost.point} points deducted"}

class FollowHome(FollowBase):
    """HOMEページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')

class FollowDetail(FollowBase):
    """詳細ページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('detail', pk)
    
class DivinerDetail(LoginRequiredMixin,DetailView, ProcessFormView):
    model = get_user_model()
    template_name = 'diviner_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = SendMessageForm()
        context['diviner'] = self.get_object() 
        context['divinertype_display'] = context['diviner'].divinertype_display

        if context['diviner'].profile_data is not None and 'img' in context['diviner'].profile_data:
            context['image_url'] = context['diviner'].profile_data["img"]
        else:
            context['image_url'] = None
        return context

    def post(self, request, *args, **kwargs):
        form = SendMessageForm(request.POST)
        if form.is_valid():
            pk = self.kwargs.get("pk")
            user = get_object_or_404(get_user_model(), id=pk)
            
            # メッセージの送信処理を加える
            message = form.cleaned_data.get("message")
            receiver = user
            sender = request.user  # 仮定として、リクエストユーザーが送信者だとします
             # Check if user is already following the user_to_follow, if not, follow
            connection, created = Connection.objects.get_or_create(user=request.user)
            if user not in connection.following.all():
                connection.follow(user)
                # Optionally, you might want to send a success message for the following action too
                messages.success(request, f'You are now following {user.username}.')
            if user.usertype == "顧客":
                action_label = "send"
                result = deduct_points(user, action_label)
                # エラー処理
                if "error" in result:
                    # エラーメッセージを表示
                    return render(request, "error.html", {"error_message": result["error"]})
            

            # メッセージオブジェクトを作成し、保存します
            message = Messages(
                description=message,
                sender_name=sender,
                sender_id=sender.id,
                receiver_id=receiver.id,
                receiver_name=receiver
            )
            message.save()

            # 成功メッセージをユーザーに表示
            messages.success(request, 'メッセージを送信しました。')
            return HttpResponseRedirect(reverse('room', args=[user.username]))
        return self.get(request, *args, **kwargs)

@login_required
def follow_diviner(request, pk):
    # ユーザを取得
    user_to_follow = get_object_or_404(get_user_model(), pk=pk)

    if request.user == user_to_follow:
        messages.error(request, '自分自身をフォローすることはできません。')
        return redirect('mydiviner')  # 適切なビュー名に変更

    # Connectionモデルを取得または作成
    connection, created = Connection.objects.get_or_create(user=request.user)
    
    # フォロー処理
    if user_to_follow not in connection.following.all():
        connection.following.add(user_to_follow)
        messages.success(request, f'{user_to_follow.username}をフォローしました。')
    else:
        messages.info(request, f'{user_to_follow.username}は既にフォローしています。')

    # 以前のページにリダイレクト
    return HttpResponseRedirect(reverse('get_message', args=[user_to_follow.username]))

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

class SearchUser(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if 'search' in request.GET:
            query = request.GET.get("search")
            user_list = User.objects.exclude(username=request.user.username).filter(username__icontains=query)
        else:
            user_list = User.objects.exclude()

        user_list = list(user_list)

        friends = getFriendsList(self)

        return render(request, "search.html", {'users': user_list, 'friends': friends,'point':self.request.user.points})

class Message(LoginRequiredMixin, View):
    
    def get(self,request, username):
            """
            特定ユーザ間のチャット情報を取得する
            """
            friend = User.objects.get(username=username)
            current_user = request.user
            chat_messages = Messages.objects.filter(
                (Q(sender_name=current_user.id) & Q(receiver_name=friend.id)) |
                (Q(sender_name=friend.id) & Q(receiver_name=current_user.id))
            )
            friends = getFriendsList(self)
            return render(request, "chat/messages.html",
                            {'chat_messages': chat_messages,
                            'friends': friends,
                            'current_user': current_user, 'friend': friend})

@login_required
def follow_user(request, user_to_follow_id):
    if request.method == "POST":  # 通常、フォローアクションはPOSTリクエストを使用します
        # 現在のユーザーとフォローしたいユーザーを取得
        user_to_follow = get_object_or_404(get_user_model(), pk=user_to_follow_id)

        # 現在のユーザーのConnectionオブジェクトを取得または作成
        connection, created = Connection.objects.get_or_create(user=request.user)

        # Connectionオブジェクトを使用してユーザーをフォロー
        connection.follow(user_to_follow)

        # そして通常、ユーザーをどこかにリダイレクトします（例: プロフィールページ）
        return redirect('profile', username=user_to_follow.username)

    else:
        # GETなど他のリクエストメソッドを不許可として、405 Method Not Allowedレスポンスを返す
        return HttpResponseNotAllowed(['POST'])

class UpdateMessage(View):
    
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        action_label = "send"
        result = deduct_points(request.user, action_label)

        receiver_user = User.objects.get(id=data["receiver_name"])

        # エラー処理
        if "error" in result:
            # エラーメッセージを表示
            print(result)
            messages.error(request, result["error"])
            redirect_url = reverse('get_message', args=[receiver_user.username])
            return JsonResponse({"redirect": redirect_url}, status=400)        
        serializer = MessageSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        
        return JsonResponse(serializer.errors, status=400)
    
from django.views.generic import FormView

class ProfileChangeView(LoginRequiredMixin, FormView):
    
    template_name = 'profile/change.html'
    form_class = ProfileChangeForm
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super().get_initial()
        profile, created = Profile.objects.get_or_create(userPro=self.request.user, defaults={'nickName': 'デフォルトユーザー'})
        initial['img'] = profile.img
        initial['introduction'] = profile.introduction
        return initial
    
    def form_valid(self, form):
        profile = Profile.objects.get(userPro=self.request.user)
        form.update(profile)
        return super().form_valid(form)
    
    def get_config_value(self,key):
        try:
            config = Config.objects.get(key=key)
            return config.value
        except Config.DoesNotExist:
            return None
    
    # テンプレート内で呼び出せる、コンテキストをセットする。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(userPro=self.request.user)
        context['username'] = self.request.user.username
        context['usertype'] = self.request.user.usertype
        context['email'] = profile.userPro.email
        context['message_count'] = Messages.objects.filter(sender_name=self.request.user).count()
        context["product_list"] = Product.objects.all()
        context["introduction"] = profile.introduction

        context["point"] = self.request.user.points

        context["account_settings_value"] = self.get_config_value('account_settings')
        context["help_value"] = self.get_config_value('help')
        context["account_deletion"] = self.get_config_value('account_deletion')
        context["pricing_system"] = self.get_config_value('pricing_system')
        context["user_manual"] = self.get_config_value('user_manual')
        context["terms_of_service"] = self.get_config_value('terms_of_service')
        context["privacy_policy"] = self.get_config_value('privacy_policy')
        context["spec_com_trans_law"] = self.get_config_value('spec_com_trans_law')
        return context
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    # ログインしているユーザーを取得
    user = request.user
    # ユーザーのis_deletedをTrueに設定
    user.is_deleted = True
    user.save()
    # ユーザーをログアウトさせる
    logout(request)
    # レスポンスを返す
    return Response(status=status.HTTP_204_NO_CONTENT)