from http import HTTPStatus

from django.contrib.auth import get_user_model
# from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    """Класс для проверки URL."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_author = User.objects.create_user(username='author_test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author_post = Client()
        cls.authorized_client_author_post.force_login(cls.user_author)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='title_test',
            slug='slug_test',
        )
        cls.post = Post.objects.create(
            text='text_post_test',
            author=cls.user_author,
            group=cls.group,
        )
        cls.url = {'index': reverse('posts:index', kwargs=None),
                   'group_list': reverse('posts:group_list',
                                         kwargs={'slug': cls.group.slug}),
                   'post_detail': reverse('posts:post_detail',
                                          kwargs={'post_id': cls.post.id}),
                   'profile_user': reverse('posts:profile',
                                           kwargs={'username': cls.user}),
                   'create_post': reverse('posts:post_create', kwargs=None),
                   'post_edit': reverse('posts:post_edit',
                                        kwargs={'post_id': cls.post.id}),
                   }


    def test_uses_correct_status_code(self):
        """Проверка доступности страниц."""
        for key in self.url:
            with self.subTest(reverse=key):
                if key == 'post_edit':
                    response = self.authorized_client_author_post.get(
                        self.url[key])
                elif key == 'create_post':
                    response = self.authorized_client.get(self.url[key])
                else:
                    response = self.guest_client.get(self.url[key])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_correct_status_code_create_no_author_post(self):
        """
        Проверка доступности страницы /create/ при редактировании поста для
        авторизованного пользователя, но не автора поста.
        """
        response = self.authorized_client.get(self.url['post_edit'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page(self):
        """Проверка доступности несущ. страницы."""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Проверка шаблонов."""
        cache.clear()
        templates_urls_name = {
            self.url['index']: 'posts/index.html',
            self.url['group_list']: 'posts/group_list.html',
            self.url['profile_user']: 'posts/profile.html',
            self.url['post_detail']: 'posts/post_detail.html',
            self.url['post_edit']: 'posts/create_post.html',
            self.url['create_post']: 'posts/create_post.html',
        }

        for address, template in templates_urls_name.items():
            with self.subTest(address=address):
                if address == self.url['create_post']:
                    response = self.authorized_client.get(address)
                elif address == self.url['post_edit']:
                    response = self.authorized_client_author_post.get(address)
                else:
                    response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
