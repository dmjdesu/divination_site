# Generated by Django 4.2.2 on 2024-01-07 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0016_messages_receiver_id_messages_sender_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Config",
            fields=[
                (
                    "key",
                    models.CharField(
                        choices=[
                            ("account_settings", "アカウント・メルマガ設定"),
                            ("help", "ヘルプ"),
                            ("account_deletion", "退会・アカウント削除"),
                            ("pricing_system", "料金システム"),
                            ("user_manual", "ユーザーマニュアル"),
                            ("terms_of_service", "利用規約"),
                            ("privacy_policy", "プライバシーポリシー"),
                            ("spec_com_trans_law", "特定商取引法に基づく表示"),
                        ],
                        max_length=50,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("value", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="receive_newsletter",
            field=models.BooleanField(default=False),
        ),
    ]