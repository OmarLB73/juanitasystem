# Generated by Django 5.0 on 2024-11-24 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0014_decorator_proyects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decorator',
            name='proyects',
            field=models.ManyToManyField(blank=True, related_name='proyects', to='proyect.proyect'),
        ),
    ]
