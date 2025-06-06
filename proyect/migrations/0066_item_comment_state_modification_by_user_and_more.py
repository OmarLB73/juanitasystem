# Generated by Django 5.0 on 2025-01-26 16:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0065_item_comment_state_item_comments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='item_comment_state',
            name='modification_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item_comment_state',
            name='modification_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
