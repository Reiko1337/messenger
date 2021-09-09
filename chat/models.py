from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.shortcuts import reverse
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    custom model user
    """
    SETTINGS_MESSAGE = (
        ('all', 'Все'),
        ('friends', 'Только друзья')
    )

    first_name = models.CharField(verbose_name='Имя', max_length=255)
    last_name = models.CharField(verbose_name='Фамилия', max_length=255)
    image = models.ImageField(verbose_name='Фотография', upload_to='user_image',
                              default='user_image/default.jpeg')
    settings_message = models.CharField(verbose_name='Кто мне может отправлять сообщения?', max_length=255,
                                        choices=SETTINGS_MESSAGE, default='all')

    def is_friend(self, user):
        friend = self.get_fiend(user)
        if friend:
            return friend.status == 'friend'
        else:
            return False

    def get_friends(self):
        return Friend.objects.filter((Q(user_1=self) | Q(user_2=self)) & Q(status='friend')).all()

    def get_friends_request(self):
        return Friend.objects.filter((Q(user_1=self) | Q(user_2=self)) & Q(status='request')).all()

    def get_fiend(self, user):
        search_friend_model_1 = self.user1.filter(user_2=user).first()
        search_friend_model_2 = self.user2.filter(user_1=user).first()
        if search_friend_model_1:
            return search_friend_model_1
        elif search_friend_model_2:
            return search_friend_model_2
        else:
            return False

    def get_friend_status(self, user):
        friend = self.get_fiend(user)
        return friend.status if friend else False

    def __str__(self):
        return '{0} ({1})'.format(self.get_full_name(), self.username)


class Friend(models.Model):
    """
    friend
    """
    STATUS = (
        ('request', 'Запрос в друзья'),
        ('friend', 'Друзья'),
        ('subscriber', 'Подписчик')
    )

    user_1 = models.ForeignKey(User, verbose_name='Пользователь 1', on_delete=models.CASCADE, related_name='user1')
    user_2 = models.ForeignKey(User, verbose_name='Пользователь 2', on_delete=models.CASCADE, related_name='user2')
    status = models.CharField(verbose_name='Статус', choices=STATUS, max_length=255, default='request')

    def __str__(self):
        return '({0}, {1})/{2}'.format(self.user_1.get_full_name(), self.user_2.get_full_name(),
                                       self.get_status_display())

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'


class ChatRoom(models.Model):
    """"
    chat room
    """
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Создатель беседы', on_delete=models.CASCADE,
                                related_name='creator')
    image = models.ImageField(verbose_name='Фотография', upload_to='chat_room_image',
                              default='chat_room_image/default.jpg')
    slug = models.SlugField(verbose_name='URL', unique=True)
    title = models.CharField(verbose_name='Название', max_length=255)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Участники чата')
    timestamp = models.DateTimeField(auto_now=True)

    message = GenericRelation('ChatRoomMessage')

    class Meta:
        verbose_name = 'Беседа'
        verbose_name_plural = 'Беседы'
        ordering = ('-timestamp',)

    def __str__(self):
        return self.title

    def connect_user(self, user):
        """
        :param user:
        :return True if user is added to the users list:
        """
        is_user_added = False
        if user not in self.users.all():
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all():
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        """
        :param user:
        :return True if user is removed to the users list:
        """
        is_user_removed = False
        if user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True
        return is_user_removed

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = 'room-{0}'.format(self.pk)
        return super().save(*args, **kwargs)

    @property
    def get_count_user(self):
        return self.users.count()

    @property
    def get_content_type(self):
        return ContentType.objects.get_for_model(self).model

    def get_title(self, user=None):
        return self.title

    def get_image(self, user=None):
        return self.image.url

    def get_absolute_url(self):
        return reverse('room', kwargs={'room_name': self.slug, 'chat': 'chatroom'})

    def get_users_without_creator(self):
        return self.users.exclude(pk=self.creator.pk).all()


class PrivateChatRoom(models.Model):
    slug = models.SlugField(verbose_name='URL', unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Участники чата',
                                   related_name='private_users')
    timestamp = models.DateTimeField(auto_now=True)

    message = GenericRelation('ChatRoomMessage')

    class Meta:
        verbose_name = 'Личное комната'
        verbose_name_plural = 'Личные комнаты'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = 'private-room-{0}'.format(self.pk)
        return super().save(*args, **kwargs)

    def get_title(self, user):
        return self.users.exclude(pk=user.pk).first().get_full_name()

    def get_absolute_url(self):
        return reverse('room', kwargs={'room_name': self.slug, 'chat': 'privatechatroom'})

    def get_image(self, user):
        return self.users.exclude(pk=user.pk).first().image.url

    @property
    def get_content_type(self):
        return ContentType.objects.get_for_model(self).model

    def __str__(self):
        return '{0} ({1}) / {2} ({3})'.format(
            self.users.first().get_full_name(),
            self.users.first(),
            self.users.last().get_full_name(),
            self.users.last()
        )

class ChatRoomMessage(models.Model):
    """
    chat room message
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(verbose_name='Сообщение')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['id']

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        self.full_clean()
        # self.content_object.save()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.content_type is ContentType.objects.get_for_model(PrivateChatRoom):
            interlocutor = self.content_object.users.exclude(pk=self.user.pk).first()
            if not (self.user.is_friend(interlocutor) or interlocutor.settings_message == 'all'):
                raise ValidationError('Вы не можете отправить сообщение - {0}'.format(interlocutor.get_full_name()))

        if self.content_type is ContentType.objects.get_for_model(ChatRoom):
            if self.user not in self.content_object.users.all():
                raise ValidationError(
                    'Вы не можете отправить сообщение в беседу - {0}'.format(self.content_object.title))
