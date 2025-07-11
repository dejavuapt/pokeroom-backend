# Generated by Django 5.2.1 on 2025-07-06 14:10

import django.contrib.postgres.fields
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
            name='GameInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('P', 'PlanningPoker'), ('R', 'Retrospective')], max_length=1, verbose_name='Game type')),
                ('status', models.CharField(choices=[('O', 'Opened'), ('S', 'Started'), ('F', 'Finished'), ('C', 'Closed')], default='O', max_length=1, verbose_name='Game status')),
                ('config', models.JSONField(default=dict, verbose_name='Config data')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('host_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_games', to=settings.AUTH_USER_MODEL, verbose_name='Hoted by')),
            ],
        ),
        migrations.CreateModel(
            name='LobbyGameState',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Stage name')),
                ('completed', models.BooleanField(default=False, verbose_name='Is completed stage')),
                ('result_data', models.JSONField(default=dict, verbose_name='Result data')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.gameinstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskEvaluationGameState',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Stage name')),
                ('completed', models.BooleanField(default=False, verbose_name='Is completed stage')),
                ('result_data', models.JSONField(default=dict, verbose_name='Result data')),
                ('tasks', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(), blank=True, default=list, size=None)),
                ('current_task', models.CharField(blank=True, null=True, verbose_name='Current task')),
                ('players_votes', models.JSONField(default=dict, verbose_name='Players votes')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.gameinstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('F', 'Facilitator'), ('P', 'Player')], default='P', max_length=1, verbose_name='Player role')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='games.gameinstance', verbose_name='Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to=settings.AUTH_USER_MODEL, verbose_name='Player')),
            ],
            options={
                'verbose_name': 'Player',
                'verbose_name_plural': 'Players',
                'constraints': [models.UniqueConstraint(fields=('user', 'game'), name='unique_game_players', violation_error_message='Unique player in that game already exist')],
            },
        ),
    ]
