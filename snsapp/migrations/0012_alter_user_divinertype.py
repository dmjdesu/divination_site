# Generated by Django 4.2.2 on 2023-10-20 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("snsapp", "0011_user_point_alter_divinertype_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="divinertype",
            field=models.ManyToManyField(
                blank=True, null=True, to="snsapp.divinertype"
            ),
        ),
    ]