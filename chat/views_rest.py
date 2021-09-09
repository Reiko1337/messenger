from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404

from . import serializers
from .models import User, ChatRoom, PrivateChatRoom, Friend
from .services import services


class AccountsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        serializer = serializers.RegistrationUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Регистрация прошла успешно',
                'user': serializers.UserSerializer(user).data
            })

        return Response(serializer.errors)


class MessagesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer_public_room = serializers.PublicChatRoomSerializer(
            services.get_chat_room_user(self.request.user),
            many=True,
            context={'request': request}
        )
        serializer_private_room = serializers.PrivateChatRoomSerializer(
            services.get_private_chat_room_user(self.request.user),
            many=True,
            context={'request': request}
        )
        return Response({
            'group_chat_room': serializer_public_room.data,
            'private_chat_room': serializer_private_room.data

        })

    @action(detail=True, methods=['GET', 'PUT', 'POST'])
    def public_chat_room(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk, users=request.user)
        if request.method == 'GET':
            return Response({
                'room': serializers.PublicChatRoomSerializer(
                    room,
                    context={'request': request}
                ).data,
                'messages': serializers.MessageSerializer(
                    room.message.all(),
                    many=True
                ).data
            })
        elif request.method == 'PUT':
            serializer = serializers.UpdatePublicChatRoomSerializer(
                room,
                data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Изменения прошли успешно',
                    'room': serializers.PublicChatRoomSerializer(
                        room,
                        context={'request': request}
                    ).data
                })
            return Response(serializer.errors)
        elif request.method == 'POST':
            serializer = serializers.AddUserPublicChatRoomSerializer(
                data=request.data,
                context={
                    'user': request.user,
                    'room': room
                }
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Успешно были добавлены новые участники',
                    'room': serializers.PublicChatRoomSerializer(
                        room,
                        context={'request': request}
                    ).data
                })
            return Response(serializer.errors)

    @action(detail=True, methods=['GET'])
    def private_chat_room(self, request, pk):
        room = get_object_or_404(PrivateChatRoom, pk=pk, users=request.user)
        return Response({
            'room': serializers.PrivateChatRoomSerializer(
                room,
                context={'request': request}
            ).data,
            'messages': serializers.MessageSerializer(
                room.message.all(),
                many=True
            ).data
        })

    def create(self, request):
        serializer = serializers.CreatePublicChatRoomSerializer(
            data=request.data,
            context={
                'user': request.user
            }
        )
        if serializer.is_valid():
            room = serializer.save()
            return Response({
                'message': 'Беседа была успешно создана',
                'room': serializers.PublicChatRoomSerializer(
                    room,
                    context={'request': request}
                ).data
            })
        return Response(serializer.errors)

    @action(detail=True, url_path='public_chat_room/leave', methods=['GET'])
    def leave(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk)
        if request.user in room.users.all():
            if room.get_count_user == 1:
                room.delete()
                return Response({
                    'message': 'Вы успешно покинули беседу. Беседа была удалена, так как вы были последний участник беседы'
                })
            else:
                if request.user == room.creator:
                    room.creator = room.get_users_without_creator().last()
                    room.save()
                room.users.remove(request.user)
                return Response({
                    'message': 'Вы успешно покинули беседу'
                })
        return Response({
            'error': 'Ошибка'
        })

    @action(detail=True, url_path='public_chat_room/(?P<pk_user>\d+)/exclude', methods=['DELETE'])
    def exclude(self, request, pk, pk_user):
        room = get_object_or_404(ChatRoom, pk=pk)
        user = get_object_or_404(User, pk=pk_user)
        if user in room.users.all() and request.user == room.creator:
            if request.user == user:
                return Response({
                    'message': 'Вы не можете выгнать сами себя'
                })
            room.users.remove(user)
            return Response({
                'message': 'Вы успешно выгнали: {0}'.format(user.get_full_name()),
                'room': serializers.PublicChatRoomSerializer(
                    room,
                    context={'request': request}
                ).data
            })
        return Response({
            'error': 'Ошибка'
        })

    @action(detail=True, url_path='public_chat_room/send', methods=['POST'])
    def send_message_public_chat_room(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk)
        serializer = serializers.MessageSendSerializer(
            data=request.data,
            context={
                'room': room,
                'user': request.user
            }
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                serializers.MessageSerializer(message).data
            )
        return Response(serializer.errors)

    @action(detail=True, url_path='private_chat_room/send', methods=['POST'])
    def send_message_private_chat_room(self, request, pk):
        room = get_object_or_404(PrivateChatRoom, pk=pk)
        serializer = serializers.MessageSendSerializer(
            data=request.data,
            context={
                'room': room,
                'user': request.user
            }
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                serializers.MessageSerializer(message).data
            )
        return Response(serializer.errors)


class UsersViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(
            serializers.UserSerializer(
                User.objects.all(),
                many=True
            ).data
        )

    def retrieve(self, request, pk=None):
        return Response(
            serializers.UserSerializer(
                get_object_or_404(User, pk=pk)
            ).data
        )


class FriendsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(
            serializers.UserSerializer(
                services.get_friends_by_user_model(request.user),
                many=True
            ).data
        )

    def retrieve(self, request, pk):
        queryset = get_object_or_404(
            services.get_friends_by_user_model(request.user),
            pk=pk
        )
        return Response(
            serializers.UserSerializer(queryset).data
        )

    @action(detail=False, url_path='(?P<pk_user>\d+)/change', methods=['POST'])
    def change(self, request, pk_user):
        user = get_object_or_404(User, pk=pk_user)
        auth_user = request.user

        status_friend = auth_user.get_friend_status(user)

        if status_friend in ('request', 'friend', 'subscriber'):
            friend_request = auth_user.get_fiend(user)
            if friend_request:
                if friend_request.user_1 == user and friend_request.status == 'subscriber':
                    friend_request.status = 'friend'
                    friend_request.save()
                    return Response({
                        'message': 'Теперь {0} в списке друзей'.format(user.get_full_name())
                    })
                else:
                    friend_request.delete()
                    return Response({
                        'message': 'Вы удалили {0} из списка друзей'.format(user.get_full_name())
                    })
            else:
                return Response({
                    'error': 'Ошибка'
                })
        else:
            Friend.objects.create(user_1=auth_user, user_2=user)
            return Response({
                'message': 'Вы отправили {0} запрос в друзья'.format(user.get_full_name())
            })

    @action(detail=True, methods=['POST'])
    def get_room_friend(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return Response({
                'error': 'Ошибка'
            })
        rooms = services.get_private_chat_room_user(user)
        if rooms:
            room = rooms.filter(users=user).first()
            if room:
                return Response({
                    'room': serializers.PrivateChatRoomSerializer(
                        room,
                        context={'request': request}
                    ).data,
                    'messages': serializers.MessageSerializer(
                        room.message.all(),
                        many=True
                    ).data
                })
        room = PrivateChatRoom()
        room.save()
        room.users.add(self.request.user, user)
        room.save()
        return Response({
            'room': serializers.PrivateChatRoomSerializer(
                room,
                context={'request': request}
            ).data,
            'messages': serializers.MessageSerializer(
                room.message.all(),
                many=True
            ).data
        })


class FriendsRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(
            serializers.UserSerializer(
                services.get_friends_request_by_user_model(request.user),
                many=True
            ).data
        )

    def retrieve(self, request, pk):
        queryset = get_object_or_404(
            services.get_friends_request_by_user_model(request.user),
            pk=pk
        )
        return Response(
            serializers.UserSerializer(queryset).data
        )

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        auth_user = request.user
        friend_request = auth_user.get_fiend(user)
        friend_request.status = 'friend'
        friend_request.save()
        return Response({
            'message': 'Вы приняли запрос в друзья от {0}'.format(user.get_full_name())
        })

    @action(detail=True, methods=['POST'])
    def decline(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        auth_user = request.user
        friend_request = auth_user.get_fiend(user)
        friend_request.status = 'subscriber'
        friend_request.save()
        return Response({
            'message': 'Вы отклонили запрос в друзья от {0}'.format(user.get_full_name())
        })
