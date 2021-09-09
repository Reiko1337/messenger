from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView
from rest_framework.authtoken.views import obtain_auth_token

from . import views_rest

from . import views

router = DefaultRouter()

router.register('accounts', views_rest.AccountsViewSet, basename='accounts-profile')
router.register('messages', views_rest.MessagesViewSet, basename='messages-user')
router.register('users', views_rest.UsersViewSet, basename='user')
router.register('friends', views_rest.FriendsViewSet, basename='friend')
router.register('friends-request', views_rest.FriendsRequestViewSet, basename='friend-request')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/accounts/login/', obtain_auth_token),

    path('', views.IndexView.as_view(), name='index'),

    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),
    path('accounts/profile/<int:pk>/', views.ProfileUser.as_view(), name='profile-user'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    path('messages/', views.MessageListView.as_view(), name='messages'),
    path('messages/search/', views.SearchChatRoom.as_view(), name='messages-search'),
    path('messages/create/', views.CreateChatRoom.as_view(), name='room-create'),
    path('messages/<str:room_name>/update/', views.ChatRoomUpdateView.as_view(), name='room_update'),
    path('messages/<str:room_slug>/leave/', views.LeaveChatRoom.as_view(), name='room_leave_user'),
    path('messages/<str:slug>/add-user/', views.AddUserChatRoom.as_view(), name='room_add_user'),
    path('messages/<str:room_slug>/<int:pk>/exclude/', views.ExcludeChatRoom.as_view(), name='room_exclude_user'),
    path('messages/<str:chat>/<str:room_name>/', views.ChatRoomView.as_view(), name='room'),

    path('friends/', views.ListFriendsView.as_view(), name='friends'),
    path('friends/search/', views.SearchFriends.as_view(), name='friends_search'),
    path('friends/change/<int:pk>/', views.AddFriendView.as_view(), name='friend-change'),

    path('friends-request/', views.ListFriendsRequestView.as_view(), name='friends-request'),
    path('friends-request/<str:decision>/<int:pk>/', views.DecisionFriendView.as_view(), name='friend-decision'),

    path('create-user-chat/<int:pk>/', views.CreateUserChat.as_view(), name='create_user_chat'),
]
