from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notification/', consumers.NotificationUser.as_asgi()),
    re_path(r'ws/messages/(?P<content_type>[-\w]+)/(?P<room_name>[-\w]+)/$', consumers.RoomConsumer.as_asgi()),
]