# Generated by Django 3.2.6 on 2021-08-30 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('chat', '0021_alter_privatechatroom_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroommessage',
            name='room',
        ),
        migrations.AddField(
            model_name='chatroommessage',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chatroommessage',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PrivateChatRoomMessage',
        ),
    ]
