# Generated by Django 5.2.3 on 2025-06-17 13:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("event", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="eventsubscription",
            name="user",
            field=models.ForeignKey(
                help_text="Utilisateur",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Utilisateur",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="eventsubscription",
            unique_together={("event", "user")},
        ),
    ]
