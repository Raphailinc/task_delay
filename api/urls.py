# api/urls.py
from django.urls import path
from .views import (
    ApiRoot,
    ClientListCreateView,
    ClientDetailView,
    CampaignListCreateView,
    CampaignDetailView,
    CampaignStatsView,
    MessageListCreateView,
    MessageDetailView,
)

urlpatterns = [
    path('', ApiRoot.as_view(), name='api-root'),
    
    # URL-маршруты для клиентов
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),

    # URL-маршруты для рассылок
    path('campaigns/', CampaignListCreateView.as_view(), name='campaign-list-create'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign-detail'),

    # URL-маршруты для статистики рассылок
    path('campaigns/stats/', CampaignStatsView.as_view(), name='campaign-stats'),
    path('campaigns/<int:pk>/stats/', CampaignStatsView.as_view(), name='campaign-stats-detail'),
    
    # URL-маршруты для старта рассылок
    path('campaigns/start/', CampaignStatsView.as_view(), name='campaign-start'),

    # URL-маршруты для сообщений
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
]
