# api/views.py

import logging
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from .models import Client, Newsletter, Message
from .serializers import ClientSerializer, NewsletterSerializer, MessageSerializer
from .services import send_message_to_external_service
from django.urls import reverse
from datetime import datetime, time
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

class ApiRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'clients': reverse('client-list-create'),
            'campaigns': reverse('campaign-list-create'),
        }, content_type='application/json')

# Представления для клиентов
class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'message': 'Client successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error while deleting client: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Представления для рассылок
class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            self.send_messages(instance)
        except Exception as e:
            logger.error(f"Error while sending messages: {e}")

    def send_messages(self, campaign):
        if campaign.start_time <= timezone.now() <= campaign.end_time and campaign.is_within_time_interval():
            clients = Client.objects.filter(tag=campaign.tag)
            for client in clients:
                message = Message.objects.create(campaign=campaign, client=client)
                try:
                    # Используем apply_async для асинхронной отправки
                    result = self.send_message_async.apply_async(args=[message.id])
                    task_id = result.id
                    logger.info(f"Task ID for message {message.id}: {task_id}")
                except Exception as e:
                    # Логирование ошибки при неудачной отправке
                    logger.error(f"Error sending message: {e}")
                    message.status = 'FAILED'
                    message.save()
                    
    def handle_exception(self, exc):
        logger.error(f"Error in CampaignListCreateView: {exc}")
        return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Обработка ошибок для остальных методов (GET, LIST, UPDATE, DELETE)
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CampaignListCreateView list: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CampaignListCreateView retrieve: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CampaignListCreateView update: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CampaignListCreateView destroy: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'message': 'Campaign successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error while deleting campaign: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'message': 'Message successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CampaignStatsView(APIView):
    def get(self, request, pk=None, format=None):
        try:
            if pk is None:
                # Получение общей статистики по рассылкам и количеству отправленных сообщений
                stats = Newsletter.objects.annotate(
                    total_messages=Count('messages'),
                    sent_messages=Count('messages', filter=Message.objects.filter(status='SENT')),
                    failed_messages=Count('messages', filter=Message.objects.filter(status='FAILED'))
                ).values('id', 'total_messages', 'sent_messages', 'failed_messages')
            else:
                # Получение статистики по конкретной рассылке
                campaign = get_object_or_404(Newsletter, pk=pk)
                stats = {
                    'id': campaign.id,
                    'total_messages': campaign.messages.count(),
                    'sent_messages': campaign.messages.filter(status='SENT').count(),
                    'failed_messages': campaign.messages.filter(status='FAILED').count(),
                }
            return Response(stats)
        except Exception as e:
            logger.error(f"Error in CampaignStatsView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'])
    def start(self, request, *args, **kwargs):
        try:
            campaigns = Newsletter.objects.filter(
                start_datetime__lte=datetime.now(),
                end_datetime__gte=datetime.now()
            )

            for campaign in campaigns:
                self.send_messages(campaign)

            return Response({'message': 'Campaigns started successfully'})
        except Exception as e:
            logger.error(f"Error in CampaignStartView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_messages(self, campaign):
        logger.info(f"Processing send_messages for campaign {campaign.id}")
        if campaign.start_datetime <= timezone.now() <= campaign.end_datetime and campaign.is_within_time_interval():
            clients = Client.objects.filter(tag=campaign.tag)
            for client in clients:
                message = Message.objects.create(campaign=campaign, client=client)
                try:
                    # Используем apply_async для асинхронной отправки
                    result = self.send_message_async.apply_async(args=[message.id])
                    task_id = result.id
                    logger.info(f"Task ID for message {message.id}: {task_id}")
                except Exception as e:
                    # Логирование ошибки при неудачной отправке
                    logger.error(f"Error sending message: {e}")
                    message.status = 'FAILED'
                    message.save()
                    
    def handle_exception(self, exc):
        logger.error(f"Error in CampaignStartView: {exc}")
        return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
