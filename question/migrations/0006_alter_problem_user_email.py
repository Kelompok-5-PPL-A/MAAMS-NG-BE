# Generated by Django 4.2 on 2025-03-06 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0005_problem_title_alter_problem_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='user_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
