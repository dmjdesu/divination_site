# Generated by Django 4.2.2 on 2024-01-07 12:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0018_alter_config_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="config",
            name="key",
            field=models.CharField(
                choices=[
                    ("account_settings", "アカウント・メルマガ設定"),
                    ("help", "ヘルプ"),
                    ("account_deletion", "退会・アカウント削除"),
                    ("pricing_system", "料金システム"),
                    ("user_manual", "ユーザーマニュアル"),
                    ("terms_of_service", "利用規約"),
                    ("privacy_policy", "プライバシーポリシー"),
                    ("spec_com_trans_law", "特定商取引法に基づく表示"),
                    ("pricing_about", "料金について"),
                    ("asset_settlement_law", "資産決済法に基づく表示"),
                    ("about_carecan", "ケアカンとは？"),
                    ("features_of_carecan", "ケアカンの特徴"),
                ],
                max_length=50,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
