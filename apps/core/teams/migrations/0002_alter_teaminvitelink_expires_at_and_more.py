# Generated by Django 5.2.1 on 2025-06-22 16:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teaminvitelink',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 6, 23, 16, 54, 1, 356046, tzinfo=datetime.timezone.utc), editable=False, verbose_name='Token expires date'),
        ),
        migrations.AlterField(
            model_name='teaminvitelink',
            name='token',
            field=models.CharField(default='5OocfLKr040yTaWoSS2ANg', editable=False, max_length=100, unique=True, verbose_name='Token'),
        ),
    ]
