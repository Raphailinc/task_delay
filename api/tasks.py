# tasks.py
import logging
from celery import shared_task
from .services import send_message_to_external_service
from .models import Message

logger = logging.getLogger(__name__)

@shared_task
def send_message_async(message_id):
    try:
        message = Message.objects.get(pk=message_id)
        logger.info(f"Processing send_message_async for message id: {message.id}")
        send_message_to_external_service(message.id)
    except Message.DoesNotExist:
        logger.error(f"Message with id {message_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing send_message_async: {e}")
