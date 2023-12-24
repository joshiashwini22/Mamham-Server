# Generated by Django 4.2.7 on 2023-12-22 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0010_rename_phonenumber_customer_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_time', models.DateTimeField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('remarks', models.CharField(max_length=100, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Preparing', 'Preparing'), ('On the Way', 'On the Way'), ('Completed', 'Completed')], default='Pending', max_length=20)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.customer')),
                ('delivery_address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.address')),
            ],
            options={
                'verbose_name': 'Custom Order',
                'verbose_name_plural': 'Custom Orders',
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(upload_to='')),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Dish',
                'verbose_name_plural': 'Dishes',
            },
        ),
        migrations.CreateModel(
            name='DishList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customization.customorder')),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customization.dish')),
            ],
            options={
                'verbose_name': 'Dish List',
                'verbose_name_plural': 'Dish Lists',
            },
        ),
    ]
