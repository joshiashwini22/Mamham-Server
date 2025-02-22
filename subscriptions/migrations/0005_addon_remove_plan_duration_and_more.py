# Generated by Django 4.2.7 on 2024-02-23 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_alter_subscriptiondeliverydetails_delivery_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='meal_images')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='plan',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='end_date',
        ),
        migrations.AddField(
            model_name='subscription',
            name='dietary_goal',
            field=models.CharField(choices=[('Regular', 'Regular Diet'), ('WeightLoss', 'Weight Loss'), ('Keto', 'Keto Meal'), ('MuscleGain', 'Gain Muscle')], default='Regular', max_length=20),
        ),
        migrations.AddField(
            model_name='subscription',
            name='duration',
            field=models.CharField(choices=[('7D', '7'), ('15D', '15'), ('30D', '30')], default='7D'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='meal_type',
            field=models.CharField(choices=[('Veg', 'Vegetarian'), ('NonVeg', 'Non Vegetarian')], default='Veg', max_length=10),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='subscriptions.plan'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='remarks',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='weeklymenu',
            name='plan',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='subscriptions.plan'),
        ),
        migrations.AlterField(
            model_name='plan',
            name='description',
            field=models.TextField(max_length=250),
        ),
        migrations.AlterField(
            model_name='weeklymenu',
            name='meals',
            field=models.ManyToManyField(blank=True, to='subscriptions.meal'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='addons',
            field=models.ManyToManyField(blank=True, to='subscriptions.addon'),
        ),
    ]
