from locust import HttpUser, task, between
import uuid
import random
import string


def generate_username():
    return 'user_' + str(uuid.uuid4()).replace('-', '')


def generate_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(10))


class UserBehavior(HttpUser):
    wait_time = between(1, 2)
    # tags = [i for i in range(1, 1000)]  # Примерный список id тегов
    # features = [i for i in range(1, 1000)]
    ch = [i for i in range(1, 1000)]

    def on_start(self):
        self.user_register()
        self.user_login()

    def user_register(self):
        self.username = generate_username()
        self.password = generate_password()
        self.client.post("/auth/users/", json={
            "username": self.username,
            "password": self.password
        })

    def user_login(self):
        with self.client.post("/auth/token/login", json={
            "username": self.username,
            "password": self.password
        }, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json()['auth_token']
            else:
                response.failure("Failed to obtain authentication token")

    @task
    def get_user_banner(self):
        if hasattr(self, 'token'):
            # Выбираем случайный tag_id и feature_id из предоставленного списка
            # tag_id = random.choice(self.tags)
            # feature_id = random.choice(self.features)
            ch = random.choice(self.ch)

            # Делаем запрос к серверу с выбранными tag_id и feature_id
            with self.client.get(f"/user_banner/?tag_id={ch+1}&feature_id={ch}",
                                 headers={"Authorization": f"Token {self.token}"},
                                 catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to retrieve banner with tag_id {ch+1} and feature_id {ch+1}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0, 1)


# from locust import HttpUser, task, between
# import json
#
# # Предполагаемые данные администратора
# ADMIN_USERNAME = 'test_jeka'
# ADMIN_PASSWORD = 'test_banner'
#
# # Предполагаемые данные пользователя
# USER_USERNAME = 'test_user'
# USER_PASSWORD = 'abc123Testing'
#
#
# class AdminTasks:
#     @staticmethod
#     def create_tag(client, token, tag_name):
#         return client.post("/tag/create/",
#                            json={"name": tag_name},
#                            headers={"Authorization": f"Token {token}"})
#
#     @staticmethod
#     def create_feature(client, token, feature_name):
#         return client.post("/feature/create/",
#                            json={"name": feature_name},
#                            headers={"Authorization": f"Token {token}"})
#
#     @staticmethod
#     def create_banner(client, token, feature_id, content, is_active, tags):
#         banner_data = {
#             "feature": feature_id,
#             "content": content,
#             "is_active": is_active,
#             "tags": tags
#         }
#         return client.post("/banner/",
#                            json=banner_data,
#                            headers={"Authorization": f"Token {token}"})
#
#
# class AdminBehavior(HttpUser):
#     wait_time = between(1, 2)
#
#     def on_start(self):
#         self.login()
#         self.tag_ids = []
#         self.feature_ids = []
#
#         # Создание 1000 тегов
#         for i in range(1, 1001):
#             tag_name = f'test_tag_{i}'
#             response = AdminTasks.create_tag(self.client, self.token, tag_name)
#             if response.status_code == 201:
#                 self.tag_ids.append(response.json()['id'])
#
#         # Создание 1000 фич
#         for i in range(1, 1001):
#             feature_name = f'test_feature_{i}'
#             response = AdminTasks.create_feature(self.client, self.token, feature_name)
#             if response.status_code == 201:
#                 self.feature_ids.append(response.json()['id'])
#
#         # Создание 1000 баннеров с вышеуказанными тегами и фичами
#         for i in range(1000):
#             banner_content = json.dumps({"text": f"Banner {i+1}"})
#             tags_for_banner = [self.tag_ids[i]]  # Можно указать более одного тега, если нужно
#             feature_for_banner = self.feature_ids[i]
#             AdminTasks.create_banner(self.client, self.token, feature_for_banner, banner_content, True, tags_for_banner)
#
#         self.logout()
#
#     def login(self):
#         with self.client.post("/auth/token/login",
#                               json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}) as response:
#             if response.status_code == 200:
#                 self.token = response.json()['auth_token']
#             else:
#                 response.failure("Admin failed to obtain token")
#
#     def logout(self):
#         self.client.post("/auth/token/logout", headers={"Authorization": f"Token {self.token}"})
#

# class UserBehavior(HttpUser):
#     wait_time = between(1, 2)
#
#     @task
#     def get_banner(self):
#         if not self.token:
#             self.login()
#
#         # Использование баннера
#         with self.client.get(f"/user_banner/?tag_id=1&feature_id=1",
#                              headers={"Authorization": f"Token {self.token}"},
#                              name="/user_banner/") as response:
#             if response.status_code != 200:
#                 response.failure("Failed to retrieve banner")
#
#     def login(self):
#         with self.client.post("/auth/users/",
#                               json={"username": USER_USERNAME, "password": USER_PASSWORD}) as response_create:
#             if response_create.status_code == 201:
#                 with self.client.post("/auth/token/login",
#                                       json={"username": USER_USERNAME, "password": USER_PASSWORD}) as response_token:
#                     if response_token.status_code == 200:
#                         self.token = response_token.json()['auth_token']
#                     else:
#                         response_token.failure("User failed to obtain token")
#             else:
#                 response_create.failure("User failed to be created")
#
#
# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     wait_time = between(1, 2)