# Generated by Django 4.2 on 2025-03-13 06:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("question", "0001_initial"),
        ("cause", "0003_delete_causes"),
    ]

    operations = [
        migrations.CreateModel(
            name="Causes",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("row", models.IntegerField()),
                ("column", models.IntegerField()),
                (
                    "mode",
                    models.CharField(
                        choices=[("PRIBADI", "pribadi"), ("PENGAWASAN", "pengawasan")],
                        default="PRIBADI",
                        max_length=20,
                    ),
                ),
                ("cause", models.CharField(max_length=120)),
                ("status", models.BooleanField(default=False)),
                ("root_status", models.BooleanField(default=False)),
                ("feedback", models.CharField(default="", max_length=50)),
                (
                    "question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="question.question",
                    ),
                ),
            ],
        ),
    ]
