# Generated by Django 4.2.2 on 2023-10-20 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shopping", "0002_remove_product_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="point",
            field=models.PositiveIntegerField(default=0),
        ),
    ]