# Generated by Django 5.1.7 on 2025-04-20 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cause", "0004_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="causes",
            name="cause",
            field=models.CharField(max_length=500),
        ),
    ]
