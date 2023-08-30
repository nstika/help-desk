# Generated by Django 4.1.2 on 2023-03-02 08:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssignTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('is_assigned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'assign_task',
            },
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('is_delete', models.BooleanField(default=False)),
                ('is_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-created_at', 'userID'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('projectID', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(max_length=100)),
                ('priority', models.CharField(max_length=50)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('thumbnail', models.FileField(upload_to='projects/thumbnails/')),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'project',
                'ordering': ['-projectID'],
                'permissions': [('project_visibility', 'Manager can view their assigned projects')],
            },
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('file', models.FileField(upload_to='projects/files/')),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'project_file',
            },
        ),
        migrations.CreateModel(
            name='ProjectNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noteID', models.CharField(blank=True, max_length=100, null=True)),
                ('note', models.TextField()),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'project_note',
                'ordering': ['-noteID'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('task_number', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('priority', models.CharField(max_length=50)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('document', models.FileField(upload_to='projects/tasks/documents/')),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'task',
                'ordering': ['-task_number'],
                'permissions': [('change_priority_task', 'Can change priority tasks')],
            },
        ),
        migrations.CreateModel(
            name='TaskComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'task_comments',
            },
        ),
        migrations.CreateModel(
            name='TaskFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('file', models.FileField(upload_to='projects/taks/files/')),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'task_file',
            },
        ),
        migrations.CreateModel(
            name='TaskProgess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('work_completion', models.FloatField()),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('taskID', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Projects.task')),
            ],
            options={
                'db_table': 'task_progress',
            },
        ),
        migrations.CreateModel(
            name='TaskNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('noteID', models.CharField(blank=True, max_length=100, null=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.today)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('taskID', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Projects.task')),
            ],
            options={
                'db_table': 'task_note',
                'ordering': ['-noteID'],
            },
        ),
    ]
