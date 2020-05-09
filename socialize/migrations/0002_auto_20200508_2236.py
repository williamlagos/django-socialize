# Generated by Django 3.0.5 on 2020-05-08 22:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socialize', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(default='', max_length=140),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birthday',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='profile',
            name='career',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='facebook_token',
            field=models.TextField(default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='profile',
            name='google_token',
            field=models.TextField(default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='profile',
            name='twitter_token',
            field=models.TextField(default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='visual',
            field=models.CharField(default='', max_length=100),
        ),
    ]
