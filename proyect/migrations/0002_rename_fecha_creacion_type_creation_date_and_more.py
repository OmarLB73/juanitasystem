# Generated by Django 5.0 on 2024-11-09 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='type',
            old_name='fecha_creacion',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='type',
            old_name='fecha_modificacion',
            new_name='modification_date',
        ),
        migrations.RenameField(
            model_name='type',
            old_name='user_creation',
            new_name='modification_user',
        ),
        migrations.RemoveField(
            model_name='type',
            name='usuario_modificacion',
        ),
    ]