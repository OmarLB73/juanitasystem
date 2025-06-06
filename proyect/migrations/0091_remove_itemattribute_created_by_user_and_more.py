# Generated by Django 5.0 on 2025-04-06 23:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0090_remove_categoryattribute_file_attribute_multiple_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemattribute',
            name='created_by_user',
        ),
        migrations.RemoveField(
            model_name='itemattribute',
            name='modification_by_user',
        ),
        migrations.RemoveField(
            model_name='itemattribute',
            name='modification_date',
        ),
        migrations.RemoveField(
            model_name='itemattribute',
            name='status',
        ),
        migrations.CreateModel(
            name='ItemAttributeNote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('attributeoption', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.attributeoption')),
                ('itemattribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.itemattribute')),
            ],
        ),
    ]
