# Generated by Django 4.2.7 on 2024-02-15 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customization', '0003_alter_dish_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]
