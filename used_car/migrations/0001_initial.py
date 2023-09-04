# Generated by Django 4.2.3 on 2023-08-25 15:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50, verbose_name='Name')),
                ('model_name', models.CharField(max_length=50, verbose_name='Model')),
                ('yom', models.DecimalField(decimal_places=0, max_digits=4, verbose_name='Year Of Manufacturing')),
            ],
            options={
                'unique_together': {('brand_name', 'model_name', 'yom')},
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Customer Name')),
                ('contact', models.CharField(max_length=10)),
                ('aadhar_no', models.CharField(max_length=12)),
                ('address', models.CharField(max_length=200)),
                ('sell_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('advance_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='UsedCar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_name', models.CharField(max_length=100, verbose_name='Name')),
                ('vehicle_no', models.CharField(max_length=100, unique=True, verbose_name='Number')),
                ('chassis_no', models.CharField(max_length=100, verbose_name='Chassis')),
                ('engine_no', models.CharField(max_length=100, verbose_name='Engine')),
                ('Finance_Name', models.CharField(max_length=100, verbose_name='Financer')),
                ('purchased_date', models.DateField(default=django.utils.timezone.now, verbose_name='DOP')),
                ('purchased_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Purchased')),
                ('status', models.CharField(choices=[('available', 'Available'), ('advanced', 'Advanced'), ('sold', 'Sold')], default='available', max_length=10, verbose_name='Availability')),
                ('noc_received', models.BooleanField(verbose_name='NOC')),
                ('comment', models.CharField(max_length=200)),
                ('brand', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='used_car.brand')),
            ],
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now=True)),
                ('transaction_car', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='used_car.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='interested_vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='used_car.usedcar', verbose_name='Vehicle'),
        ),
        migrations.CreateModel(
            name='charges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spares', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Spare')),
                ('labour', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Labour')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('used_car', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='used_car.usedcar')),
            ],
        ),
    ]
