# Generated by Django 5.0 on 2024-11-23 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0012_customer_apartment_customer_city_customer_state_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decorator',
            name='email',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='responsible',
            name='email',
            field=models.CharField(max_length=150),
        ),
    ]
