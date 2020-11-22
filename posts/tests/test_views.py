from django.core.cache import cache
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User, Follow


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='IvanIvanov')
        cls.second_user = User.objects.create_user(username='Erzhan')
        cls.authorized_client = Client()        
        cls.authorized_client.force_login(cls.user)
        cls.unauthorized_client = Client()
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='Group_for_test',
            description='Testing site elements'
        )
        cls.post_new = Post.objects.create(
            text='Text text text',
            author=cls.user,
            group=cls.group,
        ) 

    def test_unauthorized_user(self):
        response = self.unauthorized_client.get('new_post')
        self.assertEqual(response.status_code, 404)

    def test_new_post(self):
        new_group = self.group
        count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'Новый пост'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertEqual(self.post_new.author, self.user,
                         'User is not author of this publication')
        self.assertIsNotNone(self.post_new.text,
                             'The text field cannot be empty')
        self.assertEqual(self.post_new.group, new_group,
                         'The selected group does not exist')

    def test_show_post(self):
        cache.clear()
        urls = (
            reverse('index'),
            reverse('profile',
                    kwargs={
                        'username': self.user
                    }),
            reverse('post',
                    kwargs={
                        'username': self.user,
                        'post_id': self.post_new.id
                    }),
            reverse('group',
                    kwargs={
                        'slug': self.post_new.group.slug,
                    }),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                paginator = response.context.get('paginator')
                if paginator is not None:
                    self.assertEqual(paginator.count, 1)
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertEqual(response.status_code, 200)
                self.assertEqual(post.author, self.post_new.author)
                self.assertEqual(post.text, self.post_new.text)
                self.assertEqual(post.group, self.post_new.group)

    def test_img_tag(self):
        small_gif = ( 
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04" 
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02" 
            b"\x02\x4c\x01\x00\x3b")       
        img = SimpleUploadedFile( 
            "small.gif", 
            small_gif, 
            content_type="image/gif"
        ) 
        post = Post.objects.create(text='Этот с картинкой!',
                                   author=self.user,
                                   group=self.group,
                                   image=img)
        response = self.authorized_client.post(reverse('post', kwargs={
                'post_id': post.pk,
                'username': post.author 
            }   
        )
        )
        self.assertContains(
                response,
                '<img',
                status_code=200
            )

    def test_img_on_pages(self):
        cache.clear()
        small_gif = ( 
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04" 
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02" 
            b"\x02\x4c\x01\x00\x3b")       
        img = SimpleUploadedFile( 
            "small.gif", 
            small_gif, 
            content_type="image/gif"
        ) 
        post = Post.objects.create(text='Этот с картинкой!',
                                   author=self.user,
                                   group=self.group,
                                   image=img)
        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': post.author}),
            reverse(
                'post',
                kwargs={
                    'username': post.author,
                    'post_id':   post.pk,
                },
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                response_unauthorized = self.unauthorized_client.get(url)
                paginator = response.context.get('paginator')
                if paginator is not None:
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertContains(response, '<img', status_code=200)
    
    def test_img_format(self):
        with open('posts/some_file.txt', 'rb') as isnt_img:
            response = self.authorized_client.post(reverse('new_post'), {   
                'group': self.group,
                'author': self.user, 
                'text': 'post with image', 
                'image': isnt_img
            },
                follow=True
            )
        self.assertFormError(
            response,
            'form',
            'image',
            'Загрузите правильное изображение. '
            'Файл, который вы загрузили, поврежден или не является ' 
            'изображением.'
        )

    def test_auth_comment(self):

        comment_text = 'Какой-то текст'
        response = self.authorized_client.post(
            reverse('add_comment', args=[
                self.post_new.author,
                self.post_new.pk]),
            {'text': comment_text},
            follow=True
        )
        self.assertIn(
            comment_text,
            [comment.text for comment in response.context['comments']]
        )

    def test_view_post_with_follow(self):
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={
                'username': self.second_user
                }
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.second_user,                  
                user=self.user
            ).exists(),
        )

    def test_followed_authors_post_appears_in_follow_list(self):
        test_post = Post.objects.create(
            text='Новый Текст', author=self.second_user)
        Follow.objects.create(author=self.second_user,
                              user=self.user)
        with self.subTest(
                msg='Проверьте следующий пост'
                    ' автора на странице follow_index'):
            response = self.authorized_client.get(reverse('follow_index'))
            self.assertIn(
                test_post, response.context['page'])
        with self.subTest(
                msg='Проверьте следующий пост'
                    ' автора на странице follow_index'):
            Follow.objects.filter(
                author=self.second_user,
                user=self.user).delete()
            response = self.authorized_client.get(reverse('follow_index'))
            self.assertNotIn(
                test_post, response.context['page'])

    def unfollow_test(self):
        self.client.get(
            reverse('profile_unfollow', args=[
                self.second_user.username]
            )
        )
        self.assertFalse(
            Follow.objects.filter
            (author=self.second_user,
             user=self.user).exists()
        )
