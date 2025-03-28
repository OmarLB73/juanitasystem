# Generated by Django 5.0 on 2025-01-23 13:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0050_rename_created_by_type_created_by_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='created_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_types', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='type',
            name='modification_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_types', to=settings.AUTH_USER_MODEL),
        ),
    ]
