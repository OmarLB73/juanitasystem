# Generated by Django 5.0 on 2024-12-21 18:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0029_proyect_item'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('qty', models.IntegerField(null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1)),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modification_date', models.DateTimeField(auto_now=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.category')),
                ('creation_user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_creation_set', to=settings.AUTH_USER_MODEL)),
                ('modification_user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_modification_set', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.place')),
                ('proyect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.proyect')),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyect.subcategory')),
            ],
        ),
        migrations.DeleteModel(
            name='Proyect_Item',
        ),
    ]
