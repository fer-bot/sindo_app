# Generated by Django 4.0.1 on 2023-01-02 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maindashboard', '0005_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='company_number',
            field=models.CharField(default='ASD', max_length=10),
            preserve_default=False,
        ),
    ]
