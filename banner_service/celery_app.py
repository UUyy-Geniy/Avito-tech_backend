from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Указать Django использовать настройки вашего проекта по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banner_service.settings')

app = Celery('banner_service')

# Настроить приложение для использования пространства имен 'CELERY',
# чтобы все имена ключей Celery задач соответствовали данному пространству имен.
app.config_from_object('django.conf:settings')
app.conf.broker_url = settings.CELERY_BROKER_URL

# Загрузить задачи модулей task.py в django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Hello')
