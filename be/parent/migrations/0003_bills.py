# Generated by Django 4.1 on 2022-08-15 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parent', '0002_balancehistory_is_gift'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('invoince', models.CharField(max_length=100)),
                ('price', models.FloatField()),
            ],
        ),
    ]
