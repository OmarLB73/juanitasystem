# Generated by Django 5.0 on 2024-12-21 19:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0030_item_delete_proyect_item'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='notes',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
        migrations.CreateModel(
            name='Item_Attribute',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('notes', models.CharField(blank=True, max_length=150, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1)),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modification_date', models.DateTimeField(auto_now=True, null=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.attribute')),
                ('creation_user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_attribute_creation_set', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.item')),
                ('modification_user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_attribute_modification_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
