# Generated by Django 4.0.4 on 2022-07-14 21:26

from django.db import migrations, models
import superuser.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Branchs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(default='Turkiye', max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('short_description', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=400)),
                ('image', models.ImageField(blank=True, default=superuser.models.get_default_news_image, null=True, upload_to=superuser.models.get_news_image_filepath)),
                ('is_campaign', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
