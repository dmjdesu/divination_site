# Generated by Django 4.2.2 on 2023-09-28 14:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0006_user_divinertype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="divinertype",
            field=models.CharField(
                choices=[
                    ("命術_四柱推命", "命術_四柱推命"),
                    ("命術_紫微斗数", "命術_紫微斗数"),
                    ("命術_風水", "命術_風水"),
                    ("卜術_易経", "卜術_易経"),
                    ("卜術_タロット", "卜術_タロット"),
                    ("卜術_ルーン", "卜術_ルーン"),
                    ("相術_手相", "相術_手相"),
                    ("相術_顔相", "相術_顔相"),
                    ("相術_人相", "相術_人相"),
                    ("霊感_オラクルカード", "霊感_オラクルカード"),
                    ("霊感_クレアボヤント", "霊感_クレアボヤント"),
                    ("心理_心理学", "心理_心理学"),
                    ("心理_占星術", "心理_占星術"),
                ],
                max_length=30,
            ),
        ),
    ]