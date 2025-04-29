from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]
    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['email'], 'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),

        # migrations.RunSQL(
        #     sql="""
        #     CREATE OR REPLACE FUNCTION generate_username() RETURNS TRIGGER AS $$
        #     BEGIN
        #         IF NEW.username IS NULL OR NEW.username = '' THEN
        #             NEW.username := NEW.email;
        #         END IF;
        #         RETURN NEW;
        #     END;
        #     $$ LANGUAGE plpgsql;
            
        #     CREATE TRIGGER set_username_from_email
        #     BEFORE INSERT OR UPDATE ON authentication_customuser
        #     FOR EACH ROW
        #     EXECUTE FUNCTION generate_username();
        #     """,
        #     reverse_sql="""
        #     DROP TRIGGER IF EXISTS set_username_from_email ON authentication_customuser;
        #     DROP FUNCTION IF EXISTS generate_username();
        #     """
        # ),
    ]