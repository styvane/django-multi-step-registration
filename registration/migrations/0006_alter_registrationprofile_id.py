# Generated by Django 4.2.2 on 2023-06-30 02:44

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0005_activation_key_sha256"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registrationprofile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]