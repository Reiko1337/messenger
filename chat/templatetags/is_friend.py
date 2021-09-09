from django import template

register = template.Library()


@register.inclusion_tag('chat/tags/is_friend.html')
def is_friend(auth_user, user):
    status = auth_user.get_friend_status(user)
    if status == 'subscriber':
        if auth_user.get_fiend(user) and auth_user.get_fiend(user).user_1 == user:
            status = 'friend_accept'
    return {'status': status,
            'user_pk': user.pk}
