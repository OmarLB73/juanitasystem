# Generated by Django 5.0 on 2025-01-27 03:59

import proyect.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0067_alter_item_images_file_item_comment_state_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_comment_state_files',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to='files/'),
            # field=models.ImageField(blank=True, null=True, upload_to=proyect.models.get_file_path_comment),
        ),
    ]
