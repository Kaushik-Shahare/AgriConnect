# Generated by Django 5.1.2 on 2024-10-13 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crop', '0009_alter_crop_catogory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crop',
            name='catogory',
            field=models.CharField(choices=[('vegetable', 'Vegetable'), ('fruit', 'Fruit'), ('grain', 'Grain'), ('legume', 'Legume'), ('tuber', 'Tuber')]),
        ),
    ]
