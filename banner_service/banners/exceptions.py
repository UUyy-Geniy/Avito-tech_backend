from rest_framework import status
from rest_framework.views import exception_handler
from django.db import IntegrityError
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Если это IntegrityError, также возвращаем сообщение "Некорректные данные"
            if isinstance(exc, IntegrityError):
                response.data = {'error': 'Некорректные данные: дубликат'}
            else:
                response.data = {'error': 'Некорректные данные'}
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            response.data = {'error': 'Пользователь не авторизован'}
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            response.data = {'error': 'Пользователь не имеет доступа'}
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {'error': 'Баннер не найден'}
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            response.data = {'error': 'Внутренняя ошибка сервера'}

    return response


class DuplicateDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Дубликат данных'
    default_code = 'duplicate_data'
