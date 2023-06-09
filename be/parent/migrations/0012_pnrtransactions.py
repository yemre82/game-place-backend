# Generated by Django 4.1 on 2022-12-19 08:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parent', '0011_min_withdrawal_amount_tl_to_jeton_jetonhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='PNRTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField()),
                ('transaction_guid', models.CharField(default='', max_length=100)),
                ('otp', models.CharField(default='', max_length=100)),
                ('transaction_type', models.CharField(default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
