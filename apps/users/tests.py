from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import User
from .serializers import DefaultUserSerializer

client = APIClient()


class TestGet(APITestCase):
    def setUp(self):
        User.objects.create(cpf='44756054644', email='root@mail.com', password='!bF6tVmbXt9dMc#', full_name='I am root',
                            is_superuser=True, is_staff=True, role='collaborator')
        User.objects.create(cpf='23756054611', email='test@mail.com',
                            password='!bF6tVmbXt9dMc#', full_name='Pedro Henrique Santos',
                            role='collaborator')
        User.objects.create(cpf='33756054622', email='test2@mail.com',
                            password='!bF6tVmbXt9dMc#', full_name='Pedro Carlos', role='collaborator')

        user = User.objects.get(cpf='44756054644')
        client.force_authenticate(user=user)

    def test_list(self):
        response = client.get(reverse('user-list'))
        users = User.objects.all()
        serializer = DefaultUserSerializer(users, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        response = client.get(reverse('user-detail', args=['44756054644']))
        user = User.objects.get(email='root@mail.com')
        serializer = DefaultUserSerializer(user)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPost(APITestCase):
    def test_success(self):
        body = {'cpf': '44756054644', 'email': 'root@mail.com',
                'password': '!bF6tVmbXt9dMc#', 'full_name': 'I am root'}
        response = client.post(reverse('user-list'), body)
        user = User.objects.get(email='root@mail.com')
        serializer = DefaultUserSerializer(user)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid(self):
        body = {'cpf': 'invalid', 'email': 'invalid',
                'password': 'invalid', 'full_name': '0'}
        response = client.post(reverse('user-list'), body)
        validation = {'cpf': ['Ensure this field has at least 11 characters.'], 'email': ['Enter a valid email address.'], 'full_name': ['Invalid name'],
                      'password': ['This password is too short. It must contain at least 8 characters.']}

        self.assertEqual(response.json(), validation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        body = {'cpf': '44756054644', 'email': 'root@mail.com',
                'password': '!bF6tVmbXt9dMc#', 'full_name': 'I am root', 'invalid': 'invalid'}
        response = client.post(reverse('user-list'), body)
        validation = {'non_field_errors': ['Unknown field(s): invalid']}

        self.assertEqual(response.json(), validation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestPut(APITestCase):
    def setUp(self):
        User.objects.create(cpf='44756054644', email='root@mail.com', password='!bF6tVmbXt9dMc#', full_name='I am root',
                            is_staff=True, role='collaborator')
        user = User.objects.get(cpf='44756054644')
        client.force_authenticate(user=user)

    def test_success(self):
        body = {'full_name': 'I am root edited'}
        response = client.put(reverse('user-detail', args=['44756054644']), body)
        user = User.objects.get(email='root@mail.com')
        serializer = DefaultUserSerializer(user)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid(self):
        body = {'full_name': '0'}
        response = client.put(reverse('user-detail', args=['44756054644']), body)
        validation = {'full_name': ['Invalid name']}

        self.assertEqual(response.json(), validation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        body = {'cpf': '12345678900', 'password': '!bF6tVmbXt9dMc#'}
        response = client.put(reverse('user-detail', args=['44756054644']), body)
        validation = {'password': ['Cannot update password']}

        self.assertEqual(response.json(), validation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDelete(APITestCase):
    def setUp(self):
        User.objects.create(cpf='44756054644', email='root@mail.com',
                            password='!bF6tVmbXt9dMc#', full_name='I am root',
                            role='collaborator', is_staff=True)

        user = User.objects.get(email='root@mail.com')
        client.force_authenticate(user=user)

    def test_success(self):
        response = client.delete(reverse('user-detail', args=['44756054644']))
        user = User.objects.get(email='root@mail.com')
        serializer = DefaultUserSerializer(user)
        data = dict(serializer.data)

        self.assertEqual(data['is_active'], False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = client.delete(reverse('user-detail', args=['invalid']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
