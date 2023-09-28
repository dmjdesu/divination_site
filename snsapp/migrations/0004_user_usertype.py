# Generated by Django 4.2.2 on 2023-09-28 10:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0003_alter_connection_user_messages"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="userType",
            field=models.CharField(
                choices=[("占い師", "占い師"), ("顧客", "顧客")], default="占い師", max_length=10
            ),
            preserve_default=False,
        ),
    ]
