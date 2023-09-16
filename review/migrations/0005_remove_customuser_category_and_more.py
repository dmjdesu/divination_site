# Generated by Django 4.2.2 on 2023-09-16 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("review", "0004_usertype_alter_customuser_managers_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="category",
        ),
        migrations.RemoveField(
            model_name="userdetailsupplier",
            name="companyName",
        ),
        migrations.AddField(
            model_name="userdetailsupplier",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="review.category",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=255, verbose_name="占いカテゴリー"),
        ),
    ]
