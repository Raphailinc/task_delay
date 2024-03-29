# Generated by Django 3.2.18 on 2023-11-27 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20231127_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='tag',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='timezone',
            field=models.CharField(max_length=100),
        ),
    ]
