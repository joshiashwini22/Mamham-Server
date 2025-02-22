# Generated by Django 4.2.7 on 2023-12-09 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_rename_location_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomOrder',
            fields=[
                ('CustomOrderID', models.AutoField(primary_key=True, serialize=False)),
                ('CustomDate', models.DateField()),
                ('CustomDeliveryTime', models.DateTimeField()),
                ('CustomDeliveryAddress', models.TextField()),
                ('Total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CustomerID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Description', models.TextField()),
                ('Price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Image', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='CustomOrderList',
            fields=[
                ('CustomOrderDetailID', models.AutoField(primary_key=True, serialize=False)),
                ('Quantity', models.IntegerField()),
                ('Price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CustomOrderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.customorder')),
                ('DishID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.dish')),
            ],
        ),
    ]
