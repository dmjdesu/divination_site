# Generated by Django 4.2.2 on 2023-09-26 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(default=1, max_length=100, verbose_name="ユーザー名"),
            preserve_default=False,
        ),
    ]