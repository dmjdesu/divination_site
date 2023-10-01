from django.db.models import OuterRef, Subquery, Q, CharField, TextField
from django.db.models.functions import Coalesce
from django.db.models.expressions import Value, ExpressionWrapper
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser

from snsapp.form import DivinerTypeForm, ProfileChangeForm
from .serializers import MessageSerializer

from .models import Messages, Post, Connection, Profile, User


class Home(LoginRequiredMixin, ListView):
    """HOMEページで、自分以外のユーザー投稿をリスト表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        """リクエストユーザーのみ除外"""
        return Post.objects.exclude(user=self.request.user)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #get_or_createにしないとサインアップ時オブジェクトがないためエラーになる
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context
    

class MyPost(LoginRequiredMixin, ListView):
    """自分の投稿のみ表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
class MyDiviner(ListView):
    """占い師一覧を表示"""
    model = User
    template_name = 'diviner_list.html'

    def get_queryset(self):
        queryset = User.objects.filter(usertype="占い師")
        
        divinertype = self.request.GET.get('divinertype')
        if divinertype:
            queryset = queryset.filter(divinertype=divinertype)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DivinerTypeForm(self.request.GET or None)
        return context

class CreatePost(LoginRequiredMixin, CreateView):
    """投稿フォーム"""
    model = Post
    template_name = 'create.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('mypost')

    def form_valid(self, form):
        """投稿ユーザーをリクエストユーザーと紐付け"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class DetailPost(LoginRequiredMixin, DetailView):
    """投稿詳細ページ"""
    model = Post
    template_name = 'detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """投稿編集ページ"""
    model = Post
    template_name = 'update.html'
    fields = ['title', 'content']


    def get_success_url(self,  **kwargs):
        """編集完了後の遷移先"""
        pk = self.kwargs["pk"]
        return reverse_lazy('detail', kwargs={"pk": pk})
    
    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """投稿編集ページ"""
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('mypost')

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 


###############################################################
#いいね処理
class LikeBase(LoginRequiredMixin, View):
    """いいねのベース。リダイレクト先を以降で継承先で設定"""
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        related_post = Post.objects.get(pk=pk)

        if self.request.user in related_post.like.all():
            obj = related_post.like.remove(self.request.user)
        else:
            obj = related_post.like.add(self.request.user)  
        return obj


class LikeHome(LikeBase):
    """HOMEページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')


class LikeDetail(LikeBase):
    """詳細ページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        return redirect('detail', pk)
###############################################################


###############################################################
#フォロー処理
class FollowBase(LoginRequiredMixin, View):
    """フォローのベース。リダイレクト先を以降で継承先で設定"""
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target_user = Post.objects.get(pk=pk).user

        my_connection = Connection.objects.get_or_create(user=self.request.user)

        if target_user in my_connection[0].following.all():
            obj = my_connection[0].following.remove(target_user)
        else:
            obj = my_connection[0].following.add(target_user)
        return obj

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
###############################################################


class FollowList(LoginRequiredMixin, ListView):
    """フォローしたユーザーの投稿をリスト表示"""
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        """フォローリスト内にユーザーが含まれている場合のみクエリセット返す"""
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        all_follow = my_connection[0].following.all()
        return Post.objects.filter(user__in=all_follow)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context

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
       
        return render(request, "search.html", {'users': user_list, 'friends': friends})

class Message(LoginRequiredMixin, View):
    
    def get(self,request, username):
            """
            特定ユーザ間のチャット情報を取得する
            """
            friend = User.objects.get(username=username)
            current_user = request.user
            messages = Messages.objects.filter(
                (Q(sender_name=current_user.id) & Q(receiver_name=friend.id)) |
                (Q(sender_name=friend.id) & Q(receiver_name=current_user.id))
            )
            friends = getFriendsList(self)
            return render(request, "chat/messages.html",
                            {'messages': messages,
                            'friends': friends,
                            'current_user': current_user, 'friend': friend})

class UpdateMessage(View):
    
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
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
        initial['nickName'] = profile.nickName
        initial['img'] = profile.img
        return initial
    
    def form_valid(self, form):
        profile = Profile.objects.get(userPro=self.request.user)
        form.update(profile)
        return super().form_valid(form)