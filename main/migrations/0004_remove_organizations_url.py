# Generated by Django 3.0.6 on 2021-02-12 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_message_room_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizations',
            name='url',
        ),
    ]