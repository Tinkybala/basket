# Generated by Django 5.1.1 on 2024-10-24 12:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0011_delete_cronjoblog"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
