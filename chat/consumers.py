import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatRoomMessage, PrivateChatRoom
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.core.exceptions import ValidationError


class RoomConsumer(WebsocketConsumer):
    """
    send message
    """

    def connect(self):
        self.content_type = self.scope['url_route']['kwargs']['content_type']
        room_slug = self.scope['url_route']['kwargs']['room_name']
        try:
            content_type_room = get_object_or_404(ContentType, model=self.content_type)
            self.room = get_object_or_404(content_type_room.model_class(), slug=room_slug, users=self.scope['user'])
        except:
            self.close()

        self.room_name = self.room.slug

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if message:
            try:
                room_message = ChatRoomMessage.objects.create(
                    content_object=self.room,
                    user=self.scope['user'],
                    message=message
                )

                async_to_sync(self.channel_layer.group_send)(
                    self.room_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user_image': room_message.user.image.url,
                        'user_full_name': room_message.user.get_full_name(),
                    }
                )
                content_type_model = ContentType.objects.get_for_model(self.room)
                if content_type_model is ContentType.objects.get_for_model(PrivateChatRoom):
                    title = self.scope['user'].get_full_name()
                    image_url = self.scope['user'].image.url
                else:
                    title = self.room.title
                    image_url = self.room.image.url
                room_name = title
                image = image_url

                for user in self.room.users.all():
                    async_to_sync(self.channel_layer.group_send)(
                        user.username,
                        {
                            'type': 'notification_user',
                            'room_name': room_name,
                            'room_slug': self.room.slug,
                            'image': image,
                            'image_user': self.scope['user'].image.url,
                            'message': message,
                            'url': self.room.get_absolute_url()
                        }
                    )

            except ValidationError:
                self.close()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def chat_message(self, event):
        html_message = render_to_string('chat/tags/send_message.html', {
            'message': event['message'],
            'user_image': event['user_image'],
            'user_full_name': event['user_full_name'],
            'timestamp': datetime.now()
        })
        self.send(text_data=json.dumps({
            'html_message': html_message,
        }))


class NotificationUser(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']

        async_to_sync(self.channel_layer.group_add)(
            self.user.username,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.user.username,
            self.channel_name
        )

    def notification_user(self, event):
        if event:
            html_notification = render_to_string('chat/tags/notification.html', {
                'room_name': event['room_name'],
                'image': event['image'],
                'image_user': event['image_user'],
                'message': event['message'],
                'url': event['url']
            })

            html_dialog = render_to_string('chat/tags/dialog.html', {
                'room_name': event['room_name'],
                'image': event['image'],
                'image_user': event['image_user'],
                'message': event['message'],
            })

            self.send(text_data=json.dumps({
                'html_notification': html_notification,
                'html_dialog': html_dialog,
                'room_slug': event['room_slug'],
                'url': event['url']
            }))
