# tasks.py

import logging
from celery import shared_task
from .models import Message, Newsletter
from .services import send_message_to_external_service
from .utils import send_messages

logger = logging.getLogger(__name__)

@shared_task
def send_message_async(message_id, campaign_id):
    try:
        message = Message.objects.get(pk=message_id)
        campaign = Newsletter.objects.get(pk=campaign_id)

        send_message_to_external_service(message, campaign)
    except Message.DoesNotExist:
        print(f"Message with id {message_id} does not exist.")
    except Newsletter.DoesNotExist:
        print(f"Campaign with id {campaign_id} does not exist.")
    except Exception as e:
        print(f"Error sending message: {e}")

@shared_task
def start_campaign_async(campaign_id):
    try:
        campaign = Newsletter.objects.get(pk=campaign_id)
        # Отправка сообщений для рассылки
        send_messages(campaign)
    except Newsletter.DoesNotExist:
        logger.error(f"Campaign with id {campaign_id} does not exist.")
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
