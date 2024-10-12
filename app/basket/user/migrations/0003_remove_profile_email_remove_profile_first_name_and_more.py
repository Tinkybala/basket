# Generated by Django 5.1.2 on 2024-10-12 16:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_profile_delete_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="email",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="password",
        ),
        migrations.AlterField(
            model_name="profile",
            name="description",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
