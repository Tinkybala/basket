# Generated by Django 5.1.1 on 2024-10-24 04:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0010_cronjoblog"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CronJobLog",
        ),
    ]
