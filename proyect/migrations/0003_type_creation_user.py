# Generated by Django 5.0 on 2024-11-09 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0002_rename_fecha_creacion_type_creation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='creation_user',
            field=models.CharField(default='admin', max_length=50),
        ),
    ]
