from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationprofile",
            name="activated",
            field=models.BooleanField(default=False),
        ),
    ]
