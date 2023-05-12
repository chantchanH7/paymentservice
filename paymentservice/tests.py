from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import User, Order

# class test_user_login(TestCase):
#     def test_user_login_case(self):
#         self.url_login = reverse('login')
#         data = {'ID': '1','Password': 'password'}
#         c = Client()
#         response =  c.post(self.url_login, {'ID': '22', 'Password' : 'password'})
#         self.assertEqual(response.status_code, 200)

class test_user_register(TestCase):
    def test_user_register_case(self):
        self.url_register = reverse('register')
        self.user_data = {
            'Name': 'test_user',
            'Email': 'test_user@example.com',
            'Password': 'test_password',
        }
        c = Client()
        response = c.post(self.url_register, data = self.user_data, format='json')
        self.assertEqual(response.status_code, 200)

