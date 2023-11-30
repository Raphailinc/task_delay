# celery_config.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем переменную окружения CELERY_ALWAYS_EAGER в True
os.environ['CELERY_ALWAYS_EAGER'] = 'True'

# Устанавливаем модуль настроек Django по умолчанию для программы 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Work.settings')

# Создаем экземпляр Celery и настраиваем его, используя настройки из Django.
app = Celery('Work', broker='pyamqp://guest:guest@localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загружаем модули задач из всех зарегистрированных конфигураций приложений Django.
app.autodiscover_tasks()

# Поддержка асинхронных задач в Celery
app.conf.worker_pool_restarts = True
app.conf.task_reject_on_worker_lost = True
