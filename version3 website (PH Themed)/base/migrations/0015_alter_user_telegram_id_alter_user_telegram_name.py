# Generated by Django 5.1.1 on 2024-11-04 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_rename_tele_user_telegram_id_user_telegram_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telegram_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='telegram_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
