# Generated by Django 3.2.6 on 2021-08-19 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='Фамилия'),
        ),
    ]
