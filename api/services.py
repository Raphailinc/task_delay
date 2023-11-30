# api/services.py
import requests
import logging
from django.db import transaction
from .models import Message

logger = logging.getLogger(__name__)

def send_message_to_external_service(message, campaign):
    try:
        with transaction.atomic():
            message_data = {
                'key1': 'value1',
                'key2': 'value2',
            }

            logger.info(f"Sending message to external service: {message_data}")

            # Вместо реальной отправки, просто меняем статус сообщения
            message.status = 'SENT'
            message.save()

    except Message.DoesNotExist:
        logger.error(f"Message with id {message.id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending message to external service: {e}")