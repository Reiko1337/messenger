# Generated by Django 3.2.6 on 2021-08-19 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_rename_status_chatroom_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default='user_image/default_profile.jpeg', upload_to='user_image', verbose_name='Фотография'),
        ),
    ]