# Generated by Django 4.2.7 on 2023-11-28 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_rename_end_time_newsletter_end_datetime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
    ]
