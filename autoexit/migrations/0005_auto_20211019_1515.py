# Generated by Django 3.2.6 on 2021-10-19 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autoexit', '0004_auto_20211019_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanned_qr',
            name='qrcode',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='scanned_qr',
            name='time_scanned',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='cardcode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='lane',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='operator',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='pc',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='pic',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='pic2',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='plate',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='timein',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='timeindb',
            name='vehicle',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
