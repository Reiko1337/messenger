from django.db.models import Q
from itertools import chain
from chat.models import ChatRoom, PrivateChatRoom, User


def get_chat_room_user(user: object) -> list:
    """
    get the user's chat rooms
    :param user:
    :return chat room:
    """
    return ChatRoom.objects.filter(users=user).order_by('-timestamp').all()


def get_private_chat_room_user(user: object) -> list:
    """
    get the user's private chat rooms
    :param user:
    :return chat room:
    """
    return PrivateChatRoom.objects.filter(users=user).all()


def get_chat_rooms(user: object) -> list:
    """
    get the chat rooms of the user in which he is located
    :param user:
    :return chat rooms:
    """
    chat_rooms = get_chat_room_user(user)
    private_rooms = get_private_chat_room_user(user)
    return sorted(chain(chat_rooms, private_rooms), key=lambda instance: instance.timestamp, reverse=True)


def search_chat_rooms(q: str, user: object) -> list:
    """
    :param q:
    :param user:
    :return chat rooms:
    """
    public_rooms = ChatRoom.objects.filter(title__icontains=q, users=user).all()
    private_rooms_temp = get_private_chat_room_user(user)

    temp = tuple(room.users.exclude(pk=user.pk).first() for room in private_rooms_temp)
    users = User.objects.filter(
        Q(pk__in=map(lambda x: x.pk, temp)) & (Q(first_name__icontains=q) | Q(last_name__icontains=q)))
    private_rooms = private_rooms_temp.filter(users__in=users).all()
    return sorted(chain(public_rooms, private_rooms), key=lambda instance: instance.timestamp, reverse=True)


def get_friends(user: object) -> tuple:
    """
    :param user:
    :return users:
    """
    return tuple(item.user_1 if item.user_1 != user else item.user_2 for item in user.get_friends())


def get_friends_request(user: object) -> tuple:
    """
    :param user:
    :return users:
    """
    return tuple(item.user_1 if item.user_1 != user else item.user_2 for item in user.get_friends_request())


def get_friends_for_add_chat_room(user: object, room: object) -> list:
    """
    :param user:
    :param room:
    :return users:
    """
    friends = set(get_friends(user))
    friends_set = friends.difference(set(room.users.all()))
    return User.objects.filter(pk__in=map(lambda x: x.pk, friends_set)).all()


def get_user_exclude(user: object) -> list:
    """
    :param user:
    :return users:
    """
    user_exclude = list(get_friends(user)) + [user]
    return User.objects.exclude(pk__in=map(lambda x: x.pk, user_exclude))


def search_friends(q: str, user: object) -> list:
    """
    :param q:
    :param user:
    :return users:
    """
    friends_temp = get_friends(user)
    friends = User.objects.filter(
        Q(pk__in=map(lambda x: x.pk, friends_temp)) & (Q(first_name__icontains=q) | Q(last_name__icontains=q)))

    users_temp = get_user_exclude(user)
    users = users_temp.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)).all()
    return friends, users


def get_friends_by_user_model(user):
    """
    :param user:
    :return friends:
    """
    friends_temp = get_friends(user)
    return User.objects.filter(pk__in=map(lambda x: x.pk, friends_temp))


def get_friends_request_by_user_model(user):
    """
    :param user:
    :return friends:
    """
    friends_temp = get_friends_request(user)
    return User.objects.filter(pk__in=map(lambda x: x.pk, friends_temp))
