# Generated by Django 5.1.2 on 2024-10-14 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_profile_image_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image_public_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]