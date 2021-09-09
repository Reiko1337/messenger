from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import ChatRoom, User, PrivateChatRoom, ChatRoomMessage


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'image', 'first_name', 'last_name', 'settings_message')


class RegistrationUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def validate_password1(self, value):
        try:
            validate_password(value, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return value

    def validate_password2(self, value):
        try:
            validate_password(value, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Введенные пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password1']
        )
        return user


class PublicChatRoomSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer()

    class Meta:
        model = ChatRoom
        fields = ('id', 'creator', 'image', 'slug', 'users', 'title', 'timestamp')
        extra_kwargs = {
            'users': {
                'view_name': 'user-detail',
                'lookup_field': 'pk'
            }
        }


class PrivateChatRoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PrivateChatRoom
        fields = ('id', 'slug', 'users', 'timestamp')
        extra_kwargs = {
            'users': {
                'view_name': 'user-detail',
                'lookup_field': 'pk'
            }
        }


class CreatePublicChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('title', 'users')

    def validate_users(self, value):
        auth_user = self.context.get('user')
        users = [user for user in value if auth_user.is_friend(user)]
        if not users:
            raise serializers.ValidationError(
                'Вы не выбрали корректных участников беседы. В качестве учатников беседы могут выступать только друзья')
        users.append(auth_user)
        return users

    def create(self, validated_data):
        room = ChatRoom(
            title=validated_data['title'],
            creator=self.context.get('user')
        )
        room.save()
        room.users.add(*validated_data['users'])
        return room


class UpdatePublicChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('title', 'image')


class AddUserPublicChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('users',)

    def validate_users(self, value):
        auth_user = self.context.get('user')
        users = [user for user in value if auth_user.is_friend(user)]
        if not users:
            raise serializers.ValidationError(
                'Вы не выбрали корректных участников беседы. В качестве учатников беседы могут выступать только друзья')
        return users

    def create(self, validated_data):
        room = self.context.get('room')
        room.users.add(*validated_data['users'])
        return room


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoomMessage
        fields = ('user', 'message', 'timestamp')


class MessageSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoomMessage
        fields = ('message',)

    def create(self, validated_data):
        try:
            room_message = ChatRoomMessage.objects.create(
                content_object=self.context.get('room'),
                user=self.context.get('user'),
                message=validated_data['message']
            )
        except ValidationError as e:
            raise serializers.ValidationError({
                'error': e.messages
            })
        return room_message
