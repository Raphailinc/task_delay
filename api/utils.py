# utils.py

import logging
from celery import shared_task
from django.utils import timezone
from .models import Client, Message
from .services import send_message_to_external_service
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

def check_campaign_status(campaign_id):
    # Проверить, выполняется ли задача для этой рассылки
    result = AsyncResult(campaign_id)
    return result.state

@shared_task
def send_messages(campaign):
    from .tasks import send_message_async
    if hasattr(campaign, 'client_filter') and campaign.client_filter:
        for client_filter in campaign.client_filter:
            phone_number = client_filter.get('phone_number')

            # Получаем клиента из базы данных по номеру телефона
            client = Client.objects.filter(phone_number=phone_number).first()

            # Проверяем существование клиента
            if client:
                # Создаем сообщение и отправляем его асинхронно
                message_text = campaign.text_message
                message = Message.objects.create(campaign=campaign, client=client, message_text=message_text)
                try:
                    # Используем apply_async для асинхронной отправки
                    send_message_async.apply_async(args=[message.id, campaign.id])
                    logger.info(f"Message {message.id} sent asynchronously.")
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    message.status = 'FAILED'
                    message.save()
            else:
                logger.warning(f"Client with phone number {phone_number} does not exist.")
    else:
        if campaign.start_datetime > timezone.now():
            schedule_campaign_start(campaign)

@shared_task
def schedule_campaign_start(campaign):
    from .tasks import start_campaign_async
    try:
        # Используем apply_async для асинхронного старта рассылки
        start_campaign_async.apply_async(args=[campaign.id], eta=campaign.start_datetime)
        logger.info(f"Scheduled campaign start for {campaign.id} at {campaign.start_datetime}")
    except Exception as e:
        logger.error(f"Error scheduling campaign start: {e}")
