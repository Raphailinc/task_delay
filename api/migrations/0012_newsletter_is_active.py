# Generated by Django 4.2.7 on 2023-11-30 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_newsletter_message_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
