# Generated by Django 5.1.7 on 2025-05-01 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_reservation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='est_confirmee',
        ),
        migrations.AddField(
            model_name='reservation',
            name='statut',
            field=models.CharField(choices=[('en_attente', 'En attente'), ('confirmee', 'Confirmée'), ('refusee', 'Refusée')], default='en_attente', max_length=20),
        ),
    ]
