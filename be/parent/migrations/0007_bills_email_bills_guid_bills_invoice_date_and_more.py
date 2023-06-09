# Generated by Django 4.1 on 2022-08-18 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parent', '0006_bills_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='bills',
            name='email',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bills',
            name='guid',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bills',
            name='invoice_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bills',
            name='national_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bills',
            name='phone',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bills',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bills',
            name='totp',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='bills',
            name='firstname',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='bills',
            name='invoince',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='bills',
            name='lastname',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='bills',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
