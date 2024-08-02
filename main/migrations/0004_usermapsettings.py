# Generated by Django 5.0.7 on 2024-07-31 01:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_userpreferences'),
    ]

    operations = [
        migrations.CreateModel(
            name='userMapSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge', models.BooleanField(default=False)),
                ('accessibility', models.BooleanField(default=False)),
                ('autosave', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mapsettings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
