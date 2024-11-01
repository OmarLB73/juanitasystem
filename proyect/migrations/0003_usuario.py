# Generated by Django 5.0 on 2024-08-25 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0002_delete_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('usuario_id', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('estado', models.IntegerField(default=1)),
                ('usuario_creacion', models.CharField(default='admin', max_length=50)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('usuario_modificacion', models.CharField(default='admin', max_length=50)),
                ('fecha_modificacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('perfil', models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='proyect.perfil')),
            ],
        ),
    ]
