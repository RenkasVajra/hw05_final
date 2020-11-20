from django.core.cache import cache
from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User


class TestIndex_Cache(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.key = make_template_fragment_key('index_page')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Title group',
            slug='Test_group',
            description='group for tests'
        )
        cls.post = Post.objects.create(
            text='TextText', 
            author=cls.user,
            group=cls.group
        )

    def test_cache(self):
        response_before = self.authorized_client.get(reverse('index'))
        group = Group.objects.create(
            title='Title group',
            slug='test group',
            description='group for tests'
        )
        group.save()
        post = Post.objects.create(
            text='TextText', 
            author=self.user,
            group=self.group
        )
        response_after = self.authorized_client.get(reverse('index'),)
        self.assertEqual(response_before.content, response_after.content)
        cache.touch(self.key, 0)
        response_last = self.authorized_client.get(reverse('index'),)
        self.assertNotEqual(response_before.content, response_last.content)
