# Generated by Django 5.1.1 on 2024-11-04 07:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0012_alter_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="reminder_sent",
            field=models.BooleanField(default=False),
        ),
    ]
