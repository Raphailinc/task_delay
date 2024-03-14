# api/admin.py

from django.contrib import admin
from .models import Client, Newsletter, Message

admin.site.register(Client)
admin.site.register(Newsletter)
admin.site.register(Message)
