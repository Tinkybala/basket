# Generated by Django 5.1.1 on 2024-10-14 17:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0007_room_court_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="room",
            name="court_image",
        ),
        migrations.RemoveField(
            model_name="room",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="room",
            name="longitude",
        ),
    ]
