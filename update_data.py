# update_data.py
import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Work.settings")
django.setup()

from api.models import Newsletter

newsletters = Newsletter.objects.all()

for newsletter in newsletters:
    try:
        json_data = json.loads(newsletter.client_filter)
    except json.JSONDecodeError:
        json_data = {}

    newsletter.client_filter = json_data
    newsletter.save()
