# Generated by Django 3.2.6 on 2021-08-22 13:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_chatroom_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='Создатель беседы'),
        ),
    ]
