# Generated by Django 5.0 on 2025-01-23 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0047_item_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='creation_user',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='type',
            name='modification_user',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
