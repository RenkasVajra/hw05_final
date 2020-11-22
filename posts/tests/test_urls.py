from django.core.cache import cache
from django.core import paginator
import posts
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse 
from django.shortcuts import get_object_or_404 
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group


User = get_user_model()

cache.clear()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unauthorized_client = Client()
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test',
            slug='Testing_group',
            description='From England with bad tests',
            )
        cls.post = Post.objects.create(text='Text text text',
                                       author=cls.user,
                                       group=cls.group,
                                       )

    def test_homepage(self):
        
        response = self.unauthorized_client.get(reverse(
            'index',
        ),
        )
        self.assertEqual(response.status_code, 200)
    
    def test_post_edit(self):

        text = 'Text of pub'
        response = self.authorized_client.get(reverse(
                'post_edit',
                kwargs={'username': self.user,
                        'post_id': self.post.pk,
                        }
                    ),
                        follow=True
                    )
        self.assertEqual(
            response.status_code,
            200,
            'Функция post_edit неправильно работает',
        )
    
    def test_new_profile(self):

        """После регистрации пользователя создается его персональная страница"""
        response = self.authorized_client.get(reverse(
            'profile', 
            kwargs={'username': self.user}
        )
        )
        self.assertEqual(
            response.status_code,
            200,
            'Персональная страница не создается после регистрации'
        )

    def test_page_not_found(self):
        response = self.authorized_client.get('404_error')
        self.assertEqual(response.status_code,404)
        response = self.unauthorized_client.get('404_error')
        self.assertEqual(response.status_code,404)
