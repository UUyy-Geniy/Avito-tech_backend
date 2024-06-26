from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json


class BannerIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_credentials = {
            "username": "test_admin",
            "password": "abc123",
            "email": "admin@test.com"
        }
        self.admin = User.objects.create_superuser(**self.admin_credentials)
        self.admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                        self.admin_credentials["password"])
        self.setup_test_data()

    def setup_test_data(self):
        tags = ['test_tag1', 'test_tag2', 'test_tag3', 'test_tag4']
        for tag_name in tags:
            self.client.post("/tag/create/", {"name": tag_name}, format='json',
                             HTTP_AUTHORIZATION='Token ' + self.admin_token)

        features = ['test_feature1', 'test_feature2', 'test_feature3']
        for feature_name in features:
            self.client.post("/feature/create/", {"name": feature_name}, format='json',
                             HTTP_AUTHORIZATION='Token ' + self.admin_token)

        banners_data = [
            {
                "feature": 1,
                "content": json.dumps({"text": "Banner 1"}),
                "is_active": True,
                "tags": [1, 2]
            },
            {
                "feature": 2,
                "content": json.dumps({"text": "Banner 2"}),
                "is_active": True,
                "tags": [3]
            },
            {
                "feature": 3,
                "content": json.dumps({"text": "Banner 3"}),
                "is_active": False,
                "tags": [4]
            }
        ]
        for banner_data in banners_data:
            response = self.client.post("/banner/", banner_data, format='json',
                                        HTTP_AUTHORIZATION='Token ' + self.admin_token)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.post("/auth/token/logout", HTTP_AUTHORIZATION='Token ' + self.admin_token)

    def get_authorization_token(self, username, password):
        response = self.client.post("/auth/token/login", {"username": username, "password": password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()["auth_token"]

    def create_user_and_get_token(self, username, password):
        self.client.post("/auth/users/", {"username": username, "password": password})
        return self.get_authorization_token(username, password)

    def get_banner(self, token, tag_id, feature_id, use_last_revision=False):
        params = {
            'tag_id': tag_id,
            'feature_id': feature_id
        }
        if use_last_revision is not False:
            params['use_last_revision'] = 'true'
        response = self.client.get("/user_banner/", params, HTTP_AUTHORIZATION='Token ' + token)
        return response

    def _test_inactive_banner(self):
        """Тестирование получения неактивного баннера пользователем"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id=4, feature_id=3)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    #
    def _test_unauthorized_access(self):
        """Тестирование получения баннера неавторизованным пользователем"""
        response = self.get_banner(token='', tag_id=1, feature_id=1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_invalid_parameters(self):
        """Тестирование получения активного баннера пользователем с неправильными данными"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id='', feature_id=1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_no_banner_found(self):
        """Тестирование получения несуществующего баннера"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id=999, feature_id=999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _test_no_permission(self):
        """Тестирование недоступных взаимодействий с сервером пользователем"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.client.post("/tag/create/", {"name": 'no_permission'}, format='json',
                                    HTTP_AUTHORIZATION='Token ' + user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_active_banner_with_revision(self):
        """Тестирование получения баннера пользователем c актуальной и неактуальной инфомацией"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        # Создаем кэш
        response = self.get_banner(user_token, tag_id=3, feature_id=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_content = {"text": "Banner 2 Updated"}
        admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                   self.admin_credentials["password"])
        # Изменяем баннер
        response = self.client.patch('/banner/2/', {'content': json.dumps(updated_content)}, format='json',
                                     HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Берем из кэша
        response = self.get_banner(user_token, tag_id=3, feature_id=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_content = json.dumps({"text": "Banner 2"})
        self.assertEqual(response.json()["content"], expected_content)
        # Берем из бд
        upd_response = self.get_banner(user_token, tag_id=3, feature_id=2, use_last_revision=True)
        self.assertEqual(upd_response.status_code, status.HTTP_200_OK)
        self.assertEqual(upd_response.json()["content"], json.dumps(updated_content))

    def _test_banner_deletion(self):
        """Тестирование удаления баннера"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id=3, feature_id=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                   self.admin_credentials["password"])

        response = self.client.delete('/banner/2/', HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.get_banner(user_token, tag_id=3, feature_id=2, use_last_revision=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _test_banner_history(self):
        """Тестирование получения истории"""
        admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                   self.admin_credentials["password"])
        response = self.client.get('/banner/1/history/', HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        updated_content = {"text": "Banner 1 Updated"}
        response = self.client.patch('/banner/1/', {'content': json.dumps(updated_content)}, format='json',
                                     HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/banner/1/history/', HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def _test_banner_history_revertation(self):
        """Тестирование получения истории и банера и отката к конкретной версии"""
        admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                   self.admin_credentials["password"])
        response = self.client.get('/banner/1/history/', HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id=2, feature_id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_content = json.dumps({"text": "Banner 1 Updated"})
        self.assertEqual(response.json()["content"], expected_content)
        response = self.client.post('/banner/1/history/1/revert/', HTTP_AUTHORIZATION='Token ' + admin_token)
        response = self.get_banner(user_token, tag_id=2, feature_id=1, use_last_revision=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_content = json.dumps({"text": "Banner 1"})
        self.assertEqual(response.json()["content"], expected_content)

    def _test_banner_deletion_by_tag_or_feature(self):
        """Тестирование отложенного запроса на удаление баннера по тегу или фиче"""
        user_token = self.create_user_and_get_token("test_user", "abc123Testing")
        response = self.get_banner(user_token, tag_id=1, feature_id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        admin_token = self.get_authorization_token(self.admin_credentials["username"],
                                                   self.admin_credentials["password"])
        # К примеру, по тегу
        param = {'tag_id': 1}
        response = self.client.delete('/banner/', param, HTTP_AUTHORIZATION='Token ' + admin_token)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_all_cases(self):
        self._test_inactive_banner()
        self._test_unauthorized_access()
        self._test_invalid_parameters()
        self._test_no_banner_found()
        self._test_no_permission()
        self._test_active_banner_with_revision()
        self._test_banner_deletion()
        self._test_banner_history()
        self._test_banner_history_revertation()
        self._test_banner_deletion_by_tag_or_feature()
