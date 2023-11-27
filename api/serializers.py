# api/serializers.py

from rest_framework import serializers
from .models import Client, Newsletter, Message

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class NewsletterSerializer(serializers.ModelSerializer):
    text_message = serializers.CharField()
    client_filter = ClientSerializer(many=True)

    class Meta:
        model = Newsletter
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
