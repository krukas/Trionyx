# Generated by Django 2.2.1 on 2019-06-13 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trionyx', '0004_auto_20190604_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('verbose_name', models.TextField(blank=True, default='')),
                ('log_hash', models.CharField(max_length=32)),
                ('level', models.IntegerField(choices=[(50, 'Critical'), (40, 'Error'), (30, 'Warning'), (20, 'Info'), (10, 'Debug'), (0, 'Not set')])),
                ('message', models.TextField()),
                ('file_path', models.CharField(max_length=256)),
                ('file_line', models.IntegerField()),
                ('traceback', models.TextField(default='')),
                ('last_event', models.DateTimeField()),
                ('log_count', models.IntegerField(default=1)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_time', models.DateTimeField()),
                ('user_agent', models.TextField(default='')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='trionyx.Log')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
