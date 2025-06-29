# Generated by Django 5.2.1 on 2025-06-22 16:50

import datetime
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('O', 'Owner'), ('M', 'Moderator'), ('D', 'Member')], default='D', max_length=1, verbose_name='Role')),
                ('invited_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Invited date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_in', to=settings.AUTH_USER_MODEL, verbose_name='Member')),
            ],
            options={
                'verbose_name': 'Membership',
                'verbose_name_plural': 'Memberships',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(blank=True, max_length=200, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('members', models.ManyToManyField(through='teams.Membership', through_fields=('team', 'user'), to=settings.AUTH_USER_MODEL, verbose_name='Members')),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to=settings.AUTH_USER_MODEL, verbose_name='Team owner')),
            ],
            options={
                'verbose_name': 'Team',
                'verbose_name_plural': 'Teams',
            },
        ),
        migrations.AddField(
            model_name='membership',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_in', to='teams.team', verbose_name='Team'),
        ),
        migrations.CreateModel(
            name='TeamInviteLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token', models.CharField(default='u_8M7LY8Fw3n8vHCAC-NVQ', editable=False, max_length=100, unique=True, verbose_name='Token')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Token created date')),
                ('expires_at', models.DateTimeField(default=datetime.datetime(2025, 6, 23, 16, 50, 37, 426579, tzinfo=datetime.timezone.utc), editable=False, verbose_name='Token expires date')),
                ('team_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invite_link', to='teams.team', verbose_name='Team')),
            ],
            options={
                'verbose_name': 'Team invitelink',
                'verbose_name_plural': 'Team invitelinks',
            },
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(fields=('owner_id', 'name'), name='unique_lower_name_by_user', violation_error_message='That team with name is already exist.'),
        ),
        migrations.AddConstraint(
            model_name='membership',
            constraint=models.UniqueConstraint(fields=('team', 'user'), name='unique_membership', violation_error_message='Membership with that user and team is already exist.'),
        ),
    ]
