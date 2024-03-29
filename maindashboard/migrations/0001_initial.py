# Generated by Django 4.0.1 on 2022-06-28 11:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryParty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Marking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('warehousing_number', models.BigAutoField(primary_key=True, serialize=False)),
                ('quantity_unit', models.CharField(default='box', max_length=20)),
                ('product_name', models.CharField(max_length=300)),
                ('product_img', models.ImageField(blank=True, null=True, upload_to='')),
                ('entry_date', models.DateField()),
                ('volume', models.FloatField(blank=True, null=True)),
                ('weight', models.FloatField(blank=True, null=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('delivery_party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maindashboard.deliveryparty')),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('marking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maindashboard.marking')),
            ],
        ),
        migrations.CreateModel(
            name='TransferLogisticDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabinet_time', models.DateTimeField()),
                ('loading_location', models.CharField(max_length=100)),
                ('booking_number', models.BigIntegerField()),
                ('cabinet_number', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('cabinet_weight', models.IntegerField()),
                ('cabinet_type', models.CharField(max_length=50)),
                ('license_plate', models.CharField(max_length=50)),
                ('driver_phone', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransferInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_detail', models.CharField(db_index=True, max_length=200)),
                ('to_detail', models.CharField(db_index=True, max_length=200)),
                ('order_quantity', models.IntegerField()),
                ('volume', models.FloatField()),
                ('weight', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maindashboard.orderitem')),
                ('transfer_logistic_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindashboard.transferlogisticdetail')),
            ],
        ),
        migrations.CreateModel(
            name='TransferMoneyDetail',
            fields=[
                ('transfer_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='maindashboard.transferinfo')),
                ('price', models.BigIntegerField()),
                ('turnover', models.BigIntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
