# Generated by Django 5.0 on 2025-03-09 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0073_item_images_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_files',
            name='qty',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
