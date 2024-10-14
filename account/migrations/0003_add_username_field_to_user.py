from django.db import migrations, models

def set_default_username(apps, schema_editor):
    User = apps.get_model('account', 'User') 
    for user in User.objects.all():
        user.username = user.email.split('@')[0]  
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_address_user_city_user_country_user_created_at_and_more'), 
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, blank=True, null=True),  
        ),
        migrations.RunPython(set_default_username),
    ]