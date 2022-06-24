from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для тестирования."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='title_test',
            slug='slug_test',
        )

    def setUp(self):
        self.urls = {
            'index': reverse('posts:index'),
            'group_posts': reverse('posts:group_list',
                                   args=[self.group.slug]),
            'profile': reverse('posts:profile', args=[self.user]),
            'post_detail': reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}),
            'post_edit': reverse('posts:post_edit',
                                 kwargs={'post_id': self.post.id}),
            'post_create': reverse('posts:post_create'),
        }
        self.templates_page_names = {
            self.urls['index']: 'posts/index.html',
            self.urls['group_posts']: 'posts/group_list.html',
            self.urls['profile']: 'posts/profile.html',
            self.urls['post_detail']: 'posts/post_detail.html',
            self.urls['post_edit']: 'posts/create_post.html',
            self.urls['post_create']: 'posts/create_post.html',
        }
        cache.clear()


class PaginatorTestCase(BaseTestCase):
    """Класс для тестирования Paginator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.NUMBER_OF_POST = 15
        for x in range(cls.NUMBER_OF_POST):
            cls.post = Post.objects.create(
                text=f'text_post_test {x}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        """Подготовка словаря с urls для проверки paginator."""
        super().setUp()
        self.urls_paginator = {
            'index': self.urls['index'],
            'group_posts': self.urls['group_posts'],
            'profile': self.urls['profile'],
        }

    def test_correct_paginator(self):
        """Проверка paginator."""
        cache.clear()
        NUMBER_OF_POSTS_ON_SECOND_PAGE = self.NUMBER_OF_POST - (
            settings.NUM_OF_POSTS_PAGE)

        for key in self.urls_paginator:
            with self.subTest(reverse=key):
                response_1 = self.guest_client.get(self.urls_paginator[key])
                response_2 = self.guest_client.get(
                    self.urls_paginator[key] + '?page=2')
                self.assertEqual(len(response_1.context.get(
                    'page_obj')), settings.NUM_OF_POSTS_PAGE)
                self.assertEqual(len(response_2.context['page_obj']),
                                 NUMBER_OF_POSTS_ON_SECOND_PAGE)


class PostViewsTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='text_post_test',
            author=cls.user,
            group=cls.group,
        )
        cls.number_of_posts = Post.objects.count()
        cls.form_name = 'PostForm'

    def test_page_correct_templates(self):
        """URL использует нужный шаблон для приложения Posts."""
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                if (reverse_name == self.urls['post_edit']
                        or reverse_name == self.urls['post_create']):
                    response = self.authorized_client.get(reverse_name)
                else:
                    response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_index_context(self):
        """Проверка корректной передачи context для index.html."""
        response = self.guest_client.get(self.urls['index'])

        self.assertEqual(len(response.context.get(
            'page_obj')), self.number_of_posts)

        self.checking_the_post(self.urls['index'])

    def test_correct_group_post_context(self):
        """Проверка корректной передачи context для group_list.html."""
        response = self.guest_client.get(self.urls['group_posts'])

        self.assertEqual(response.context.get('group').title,
                         'title_test')

        self.assertEqual(len(response.context.get(
            'page_obj')), self.number_of_posts)

        self.checking_the_post(self.urls['group_posts'])

    def test_correct_profile_context(self):
        """Проверка корректной передачи context для profile.html."""
        response = self.guest_client.get(self.urls['profile'])

        self.assertEqual(response.context.get('author').username,
                         'test_user')
        self.assertEqual(len(response.context.get(
            'page_obj')), self.number_of_posts)

        self.checking_the_post(self.urls['profile'])

    def test_correct_post_detail_context(self):
        """Проверка корректной передачи context для post_detail.html."""
        response = self.guest_client.get(self.urls['post_detail'])

        self.assertEqual(response.context.get('post').id, self.post.id)

    def test_correct_post_edit_context(self):
        """Проверка корректной передачи context create_post.html."""
        """Для редактирования поста, отфильтрованного по id"""
        response = self.authorized_client.get(self.urls['post_edit'])

        self.assertEqual(response.context.get(
            'form').instance.id, self.post.id)
        self.assertEqual(response.context.get(
            'form').__class__.__name__, self.form_name)
        self.assertEqual(response.context.get(
            'is_edit'), bool(True))

    def test_correct_post_create_context(self):
        """Проверка корректной передачи context create_post.html."""
        """Создание поста."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        response = self.authorized_client.get(self.urls['post_create'])

        self.assertEqual(response.context.get(
            'form').__class__.__name__, self.form_name)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_with_a_group(self):
        """
        Проверка, что если при создании поста указать группу, то этот пост
        появляется:
        •	на главной странице сайта,
        •	на странице выбранной группы,
        Проверка, что этот пост не попал в группу, для которой не был
        предназначен.
        """
        self.group = Group.objects.create(
            title='title_test_2',
            slug='slug_test_2',
        )
        TEST_SLUG = 'slug_test_2'
        NUMBER_OF_POST_WITH_NEW_GROUP = 0

        response = self.guest_client.get(self.urls['index'])
        response_1 = self.guest_client.get(self.urls['group_posts'])
        response_2 = self.guest_client.get(reverse('posts:group_list',
                                                   args=[TEST_SLUG]))

        self.assertEqual(response.context.get('page_obj').object_list[0],
                         self.post)
        self.assertEqual(response_1.context.get('page_obj').object_list[0],
                         self.post)
        self.assertEqual(len(response_2.context.get('page_obj').object_list),
                         NUMBER_OF_POST_WITH_NEW_GROUP)

    def checking_the_post(self, urls):
        """Проверка данных поста"""
        cache.clear()
        response = self.guest_client.get(urls)

        date = response.context.get('page_obj').object_list[0].pub_date
        self.assertEqual(date, self.post.pub_date, 'Ошибка в поле дата')

        author = response.context.get('page_obj').object_list[0].author
        self.assertEqual(author, self.post.author,
                         'Ошибка в поле создатель поста')

        group = response.context.get('page_obj').object_list[0].group
        self.assertEqual(group, self.post.group, 'Ошибка в поле GROUP')

        text = response.context.get('page_obj').object_list[0].text
        self.assertEqual(text, self.post.text, 'Ошибка в поле текст поста')
