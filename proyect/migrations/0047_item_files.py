# Generated by Django 5.0 on 2025-01-14 21:35

import django.db.models.deletion
import django.utils.timezone
import proyect.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0046_item_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item_Files',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.ImageField(blank=True, null=True, upload_to='files/')),
                # ('file', models.ImageField(blank=True, null=True, upload_to=proyect.models.get_file_path_file)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('type', models.IntegerField(choices=[(1, 'Image'), (2, 'Material'), (3, 'Comment')], default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.item')),
            ],
        ),
    ]
