# Generated by Django 5.2.4 on 2025-07-25 04:44

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], max_length=10)),
                ('points', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('time_limit', models.IntegerField(default=1, help_text='Time limit in seconds')),
                ('memory_limit', models.IntegerField(default=256, help_text='Memory limit in MB')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('input_format', models.TextField(blank=True, help_text='Describe the input format')),
                ('output_format', models.TextField(blank=True, help_text='Describe the output format')),
                ('constraints', models.TextField(blank=True, help_text='List the constraints')),
                ('sample_input', models.TextField(help_text='Example input for this problem')),
                ('sample_output', models.TextField(help_text='Expected output for the above input')),
            ],
            options={
                'ordering': ['difficulty', 'points'],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('language', models.CharField(choices=[('python', 'Python'), ('java', 'Java'), ('cpp', 'C++')], max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('accepted', 'Accepted'), ('wrong', 'Wrong Answer'), ('error', 'Runtime Error'), ('timeout', 'Time Limit Exceeded')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('execution_time', models.FloatField(blank=True, null=True)),
                ('memory_used', models.IntegerField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
