# Generated by Django 5.0 on 2025-06-21 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0108_calendartaskcommentfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='description',
            field=models.TextField(blank=True, default='', max_length=2000, null=True),
        ),
    ]
