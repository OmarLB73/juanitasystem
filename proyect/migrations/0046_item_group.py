# Generated by Django 5.0 on 2025-01-13 03:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0045_alter_event_proyect'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyect.group'),
        ),
    ]
