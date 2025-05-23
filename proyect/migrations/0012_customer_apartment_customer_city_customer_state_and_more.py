# Generated by Django 5.0 on 2024-11-21 16:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0011_alter_category_status_alter_customer_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='apartment',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='city',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='state',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='zipcode',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='decorator',
            name='id_user',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='customer',
            name='description',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='address',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='apartment',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='city',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='description',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='email',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='phone',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='state',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='decorator',
            name='zipcode',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='proyect',
            name='description',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='proyect',
            name='responsible',
            field=models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.SET_NULL, to='proyect.responsible'),
        ),
    ]
