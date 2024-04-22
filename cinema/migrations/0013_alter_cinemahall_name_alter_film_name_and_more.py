# Generated by Django 4.2 on 2024-04-22 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema', '0012_alter_session_end_time_alter_session_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cinemahall',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_time',
            field=models.TimeField(default='00:02'),
        ),
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.TimeField(default='00:02'),
        ),
    ]