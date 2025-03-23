from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RunSQL(
            sql="ALTER TABLE authentication_customuser ALTER COLUMN username DROP NOT NULL;",
            reverse_sql="ALTER TABLE authentication_customuser ALTER COLUMN username SET NOT NULL;",
        ),
    ]