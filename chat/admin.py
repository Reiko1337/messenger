from django.contrib import admin
from .models import ChatRoom, ChatRoomMessage, User, Friend, PrivateChatRoom


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'get_full_name')


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_1', 'user_2', 'status')


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    filter_horizontal = ('users',)
    readonly_fields = ('slug',)


@admin.register(ChatRoomMessage)
class ChatRoomMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message',)


@admin.register(PrivateChatRoom)
class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_users')
    filter_horizontal = ('users',)
    readonly_fields = ('slug',)

    def get_users(self, rec):
        return '{0} ({1}) / {2} ({3})'.format(
            rec.users.first().get_full_name(),
            rec.users.first(),
            rec.users.last().get_full_name(),
            rec.users.last()
        )

    get_users.short_description = 'Участники'
