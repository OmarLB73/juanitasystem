# Generated by Django 5.0 on 2024-11-23 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0013_alter_decorator_email_alter_responsible_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='decorator',
            name='proyects',
            field=models.ManyToManyField(blank=True, null=True, related_name='proyects', to='proyect.proyect'),
        ),
    ]
