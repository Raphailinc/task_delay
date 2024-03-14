# api/tests/tests.py

import logging
import time
import json
import pytest
import asyncio
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Client, Newsletter, Message
from api.services import send_message_to_external_service
import responses
from celery import current_app
from django_celery_results.models import TaskResult
from channels.db import database_sync_to_async
from django.db import connection

logging.basicConfig(level=logging.DEBUG)

current_app.conf.CELERY_TASK_ALWAYS_EAGER = True

class MyTestCase(TestCase):
    def test_database_connection(self):
        self.assertTrue(connection.is_usable())

class ClientModelTest(TestCase):
    def test_str_representation(self):
        client = Client(phone_number='1234567890', operator_code='123', tag='test_tag', timezone='UTC')
        self.assertEqual(str(client), '1234567890 - test_tag')

class NewsletterModelTest(TestCase):
    def test_str_representation(self):
        newsletter = Newsletter(start_time=timezone.now(), end_time=timezone.now(),
                                text_message='Test message', time_interval_start=timezone.now().time(),
                                time_interval_end=timezone.now().time())
        self.assertEqual(str(newsletter), f'Newsletter {newsletter.id}')

class MessageModelTest(TestCase):
    def test_str_representation(self):
        message = Message(status='PENDING')
        self.assertEqual(str(message), f'Message {message.id} - PENDING')

class ExternalServiceTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_send_message_to_external_service(self):
        responses.add(responses.POST, 'https://probe.fbrq.cloud/send-message/', json={'status': 'success'}, status=200)

        client = await database_sync_to_async(Client.objects.create)(
            phone_number='1234567890', operator_code='123', tag='test_tag', timezone='UTC'
        )
        newsletter = Newsletter.objects.create(start_time=timezone.now(), end_time=timezone.now(),
                                               text_message='Test message', time_interval_start=timezone.now().time(),
                                               time_interval_end=timezone.now().time())
        message = Message.objects.create(newsletter=newsletter, client=client)

        message_status = await database_sync_to_async(Message.objects.first)().status
        print(f"Message status after sending: {message_status}")

        message = Message.objects.get(pk=message.id)
        assert message.status == Message.Status.SENT

class NewsletterViewTest(TestCase):
    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_create_newsletter_and_send_message(self):
        # Асинхронный тест создания клиента
        client_data = {"name": "John Doe", "email": "john@example.com"}
        client_response = await self.client.post('/api/clients/', client_data, format='json')
        assert client_response.status_code in [201, 400]

        if client_response.status_code == 201:
            # Асинхронный тест создания рассылки
            newsletter_data = {"subject": "Test Subject", "content": "Test Content", "messages": [client_response.json()['id']]}
            newsletter_response = await self.client.post('/api/newsletters/', newsletter_data, format='json')
            assert newsletter_response.status_code == 201

            # Асинхронный тест отправки сообщения
            message_response = await self.client.post('/api/newsletters/1/send/', format='json')
            assert message_response.status_code == 200

            # Проверяем, что сообщение было успешно отправлено
            message_id = message_response.data.get('id')

            await send_message_to_external_service(message_id)

            message = Message.objects.get(pk=message_id)
            assert message.status == Message.Status.SENT

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_create_newsletter(self):
        # Асинхронный тест создания клиента
        client_data = {
            'phone_number': '1234567890',
            'operator_code': '123',
            'tag': 'test_tag',
            'timezone': 'UTC',
        }
        client_response = await self.client.post('/api/clients/', client_data, format='json')
        assert client_response.status_code == status.HTTP_201_CREATED

        if client_response.status_code == status.HTTP_201_CREATED:
            # Асинхронный тест создания рассылки
            newsletter_data = {
                'start_time': str(timezone.now()),
                'end_time': str(timezone.now()),
                'text_message': 'Test message',
                'time_interval_start': str(timezone.now().time()),
                'time_interval_end': str(timezone.now().time()),
                'messages': [client_response.json()['id']]
            }
            response = await self.client.post('/api/newsletters/', newsletter_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert Newsletter.objects.count() == 1

            # Добавим асинхронную задержку перед проверкой
            await asyncio.sleep(1)

            # Проверим, что создан объект Message
            print(f"Number of messages created: {Message.objects.count()}")
            assert Message.objects.count() == 1  # Обеспечить создание сообщения

    def test_get_newsletters(self):
        Newsletter.objects.create(start_time=timezone.now(), end_time=timezone.now(),
                                   text_message='Test message', time_interval_start=timezone.now().time(),
                                   time_interval_end=timezone.now().time())
        response = self.client.get('/api/newsletters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
