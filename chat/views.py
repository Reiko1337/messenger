from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View, ListView, UpdateView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatRoom, ChatRoomMessage, User, Friend, PrivateChatRoom
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseNotFound

from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from .services import services
from . import forms


class IndexView(TemplateView):
    template_name = 'chat/index.html'


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    view profile user (update profile)
    """
    model = User
    template_name = 'chat/profile.html'
    form_class = forms.ProfileUpdateForm
    success_url = reverse_lazy('profile')

    def get_initial(self):
        user = self.request.user
        initial = {
            'last_name': user.last_name,
            'first_name': user.first_name,
            'settings_message': user.settings_message
        }
        return initial

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUser(LoginRequiredMixin, TemplateView):
    template_name = 'chat/profile_user.html'

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=pk)
        context['profile_user'] = user
        return context


class UserLoginView(LoginView):
    """
    view user login view
    """

    template_name = 'chat/login.html'
    authentication_form = forms.LoginForm


class SignUpView(CreateView):
    """
    view user registration
    """
    template_name = 'chat/signup.html'
    form_class = forms.SignUpForm
    model = User
    success_url = reverse_lazy('login')


class MessageListView(LoginRequiredMixin, ListView):
    """
    view list chat room
    """
    template_name = 'chat/list_chat_room.html'
    model = ChatRoom
    context_object_name = 'rooms'

    def get_queryset(self):
        return services.get_chat_rooms(self.request.user)


class SearchChatRoom(LoginRequiredMixin, View):
    """
    search chat room
    """

    def get(self, request):
        if request.is_ajax():
            q = request.GET.get('q', '')
            rooms = services.search_chat_rooms(q, request.user)
            return JsonResponse({'htmlData': render_to_string(
                'chat/tags/chat_room.html', {
                    'rooms': rooms,
                    'user': request.user
                }
            )}, status=200, safe=False)
        return JsonResponse({'success': False}, status=404)


class CreateChatRoom(LoginRequiredMixin, CreateView):
    """
    create chat room
    """
    template_name = 'chat/create_chat_room.html'
    form_class = forms.CreateChatRoomForm
    model = ChatRoom

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['friends'] = services.get_friends(user)
        return context

    def form_valid(self, form):
        users = [friend for friend in self.request.POST.getlist('users')
                 if self.request.user.is_friend(get_object_or_404(User, pk=friend))]
        if not users:
            messages.error(self.request, 'Вы не выбрали участников беседы')
            return self.form_invalid(form)
        chat_room_model = form.save(commit=False)
        chat_room_model.creator = self.request.user
        chat_room_model.save()
        chat_room_model.users.add(*users, self.request.user)
        return redirect(chat_room_model.get_absolute_url())


class ChatRoomUpdateView(LoginRequiredMixin, UpdateView):
    """
    chat room update
    """
    model = ChatRoom
    form_class = forms.ChatRoomUpdateForm
    slug_url_kwarg = 'room_name'


class LeaveChatRoom(LoginRequiredMixin, View):
    """
    leave chat room
    """

    def get(self, request, room_slug):
        room = get_object_or_404(ChatRoom, slug=room_slug)
        if request.user in room.users.all():
            if room.get_count_user == 1:
                room.delete()
            else:
                if request.user == room.creator:
                    room.creator = room.get_users_without_creator().last()
                    room.save()
                room.users.remove(request.user)
        return redirect('messages')


class AddUserChatRoom(LoginRequiredMixin, View):
    """
    add user chat room
    """
    template_name = 'chat/add_users_chat_room.html'

    def get_chat_room(self):
        room = get_object_or_404(ChatRoom, slug=self.kwargs.get('slug'))
        return room

    def get_queryset(self):
        user = self.request.user
        room = self.get_chat_room()
        return services.get_friends_for_add_chat_room(user, room)

    def get(self, request, slug):
        context = {
            'friends': self.get_queryset()
        }
        return render(request, self.template_name, context)

    def post(self, request, slug):
        users_post = request.POST.getlist('users')
        users = [friend for friend in users_post if request.user.is_friend(get_object_or_404(User, pk=friend))]
        if users:
            room = get_object_or_404(ChatRoom, slug=slug)
            room.users.add(*users)
            return redirect(room.get_absolute_url())
        else:
            messages.error(request, 'Необходимо выбрать, кого хотите добавить')
        return redirect('room_add_user', slug=slug)


class ExcludeChatRoom(LoginRequiredMixin, View):
    """
    exclude chat room
    """

    def get(self, request, room_slug, pk):
        room = get_object_or_404(ChatRoom, slug=room_slug)
        user = get_object_or_404(User, pk=pk)
        if user in room.users.all() and request.user == room.creator:
            if request.user == user:
                return redirect('room_leave_user', room_slug=room_slug)
            room.users.remove(user)
        else:
            HttpResponseNotFound(request)
        return redirect(room.get_absolute_url())


class ChatRoomView(LoginRequiredMixin, ListView):
    """
    chat room view
    """
    model = ChatRoomMessage
    template_name = 'chat/chat_room.html'
    context_object_name = 'messages_room'

    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        if self.request.user not in self.get_chat_room().users.all():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_chat_room(self):
        content_type = get_object_or_404(ContentType, model=self.kwargs.get('chat'))
        room_slug = self.kwargs.get('room_name')
        room = get_object_or_404(content_type.model_class(), slug=room_slug)
        return room

    def get_queryset(self):
        room = self.get_chat_room()
        return room.message.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        auth_user = self.request.user
        room = self.get_chat_room()
        context['access'] = True
        if self.kwargs.get('chat') == 'chatroom':
            context['form'] = forms.ChatRoomUpdateForm(initial={
                'title': room.title
            })
        else:
            user = room.users.exclude(pk=self.request.user.pk).first()
            if auth_user.is_friend(user) or user.settings_message == 'all':
                context['access'] = True
            else:
                context['access'] = False
        context['room'] = room
        return context


class ListFriendsView(LoginRequiredMixin, ListView):
    """
    list friends view
    """
    template_name = 'chat/friends.html'
    model = Friend
    context_object_name = 'friends'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        context['users'] = services.get_user_exclude(user)

        return context

    def get_queryset(self):
        user = self.request.user
        return services.get_friends(user)


class SearchFriends(LoginRequiredMixin, View):
    """
    search friends
    """

    def get(self, request):
        if request.is_ajax():
            q = request.GET.get('q', '')

            friends, users = services.search_friends(q, request.user)

            html_friends = render_to_string(
                'chat/tags/friends_list.html', {
                    'friends': friends,
                    'user': request.user
                }
            )

            html_friends_global = render_to_string(
                'chat/tags/friends_global_list.html', {
                    'users': users,
                    'user': request.user
                }
            )

            return JsonResponse({
                'htmlFriendsData': html_friends,
                'htmlFriendsGlobalData': html_friends_global
            }, status=200, safe=False)
        return JsonResponse({'success': False}, status=404)


class AddFriendView(LoginRequiredMixin, View):
    """
    add friends
    """

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        auth_user = request.user
        status_friend = auth_user.get_friend_status(user)
        if status_friend in ('request', 'friend', 'subscriber'):
            friend_request = auth_user.get_fiend(user)
            if friend_request:
                if friend_request.user_1 == user and friend_request.status == 'subscriber':
                    friend_request.status = 'friend'
                    friend_request.save()
                else:
                    friend_request.delete()
            else:
                return HttpResponseNotFound(request)
        else:
            Friend.objects.create(user_1=auth_user, user_2=user)
        return redirect('friends')


class ListFriendsRequestView(LoginRequiredMixin, ListView):
    """
    list friends request view
    """
    template_name = 'chat/friends_request.html'
    model = Friend
    context_object_name = 'friends_request'

    def get_queryset(self):
        user = self.request.user
        return services.get_friends_request(user)


class DecisionFriendView(LoginRequiredMixin, View):
    """
    decision friend view
    """

    def get(self, request, decision, pk):
        user = get_object_or_404(User, pk=pk)
        auth_user = request.user
        friend_request = auth_user.get_fiend(user)
        if friend_request:
            if friend_request.status == 'request':
                if decision in ('accept', 'decline'):
                    if decision == 'accept':
                        friend_request.status = 'friend'
                        friend_request.save()
                    else:
                        friend_request.status = 'subscriber'
                        friend_request.save()
                else:
                    HttpResponseNotFound(request)
            else:
                return HttpResponseNotFound(request)
        else:
            return HttpResponseNotFound(request)
        return redirect('friends-request')


class CreateUserChat(LoginRequiredMixin, View):
    """
    create user chat
    """

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return HttpResponseNotFound(request)
        rooms = services.get_private_chat_room_user(user)
        if rooms:
            room = rooms.filter(users=user).first()
            if room:
                return redirect(room.get_absolute_url())
        room = PrivateChatRoom()
        room.save()
        room.users.add(self.request.user, user)
        room.save()
        return redirect(room.get_absolute_url())
