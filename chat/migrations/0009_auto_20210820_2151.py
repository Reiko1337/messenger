# Generated by Django 3.2.6 on 2021-08-20 18:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_auto_20210820_2106'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatroommessage',
            options={'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterField(
            model_name='user',
            name='friends',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL, verbose_name='Друзья'),
        ),
    ]
