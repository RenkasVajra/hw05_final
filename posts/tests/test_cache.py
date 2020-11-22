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
        first = self.authorized_client.get(reverse('index'))
        Post.objects.create(text='Cache check', author=self.user)
        second = self.authorized_client.get(reverse('index'))
        cache.clear()
        third = self.authorized_client.get(reverse('index'))
        self.assertEqual(first.content, second.content)
        self.assertNotEqual(second.content, third.content)
