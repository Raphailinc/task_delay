# Generated by Django 4.2.7 on 2023-11-27 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_newsletter_client_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='client_filter',
            field=models.JSONField(default=list),
        ),
    ]
