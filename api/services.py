# api/services.py
import requests
import logging
from django.conf import settings
from django.db import transaction
from .models import Message

logger = logging.getLogger(__name__)

def send_message_to_external_service(message_id):
    try:
        with transaction.atomic():
            message = Message.objects.select_for_update().get(pk=message_id)

            message_data = {
                'key1': 'value1',
                'key2': 'value2',
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.TEST_ACCESS_TOKEN}',
            }

            logger.info(f"Sending message to external service: {message_data}")
            response = requests.post('https://probe.fbrq.cloud/send-message/', json=message_data, headers=headers)
            logger.info(f"Response from external service: {response.text}")

            if response.status_code == 200:
                message.status = 'SENT'
            else:
                message.status = 'FAILED'
                # Добавляем логику для отложенной повторной отправки
                tasks.retry_send_message.delay(message_id)

            message.save()

    except Message.DoesNotExist:
        logger.error(f"Message with id {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending message to external service: {e}")
