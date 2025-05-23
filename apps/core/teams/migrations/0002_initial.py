# Generated by Django 5.2.1 on 2025-05-13 12:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teams', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='owner_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to=settings.AUTH_USER_MODEL, verbose_name='Team owner'),
        ),
        migrations.AddField(
            model_name='teaminvitelink',
            name='team_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invite_link', to='teams.team', verbose_name='Team'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='team_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_in', to='teams.team', verbose_name='Team'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_in', to=settings.AUTH_USER_MODEL, verbose_name='Member'),
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(through='teams.TeamMember', through_fields=('team_id', 'user_id'), to=settings.AUTH_USER_MODEL, verbose_name='Members'),
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(fields=('owner_id', 'name'), name='unique_lower_name_by_user', violation_error_message='That team with name is already exist.'),
        ),
    ]
