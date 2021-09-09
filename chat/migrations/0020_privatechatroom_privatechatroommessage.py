# Generated by Django 3.2.6 on 2021-08-27 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0019_auto_20210824_2241'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Участники чата')),
            ],
            options={
                'verbose_name': 'Личное комната',
                'verbose_name_plural': 'Личные комнаты',
            },
        ),
        migrations.CreateModel(
            name='PrivateChatRoomMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.privatechatroom', verbose_name='Комната чата')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]