from django import template
from django.shortcuts import get_object_or_404
from chat.models import PrivateChatRoom, ChatRoom, User
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter()
def get_title_room(value, pk):
    content_type_model = ContentType.objects.get_for_model(value)
    if content_type_model is ContentType.objects.get_for_model(PrivateChatRoom):
        auth_user = get_object_or_404(User, pk=pk)
        title = value.get_title(auth_user)
    else:
        title = value.title
    return title


@register.filter()
def get_image_room(value, pk):
    content_type_model = ContentType.objects.get_for_model(value)
    if content_type_model is ContentType.objects.get_for_model(PrivateChatRoom):
        auth_user = get_object_or_404(User, pk=pk)
        image_url = value.get_image(auth_user)
    else:
        image_url = value.image.url
    return image_url
