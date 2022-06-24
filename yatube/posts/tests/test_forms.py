from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class FormsTestCase(TestCase):
    """Класс для тестирования форм."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='title_test',
            slug='slug_test',
        )

        cls.post = Post.objects.create(
            text='1_text_post_test',
            author=cls.user,
            group=cls.group,
        )

    def test_new_post(self):
        """Проверка создания поста."""
        cache.clear()
        post_count = Post.objects.count()
        form_data = {
            'text': '2_text_post_test',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    )

        response = self.authorized_client.get(reverse('posts:index'))
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.context.get('page_obj').object_list[0].group,
                         self.post.group)
        self.assertEqual(response.context.get('page_obj').object_list[0].text,
                         form_data['text'])
        self.assertEqual(
            response.context.get('page_obj').object_list[0].author,
            self.post.author)

    def test_edit_post(self):
        """Проверка редактирования поста."""
        group_test = Group.objects.create(
            title='title_test_1',
            slug='slug_test_1',
        )
        form_data = {
            'text': '2_text_post_test',
            'group': group_test.id
        }
        self.authorized_client.post(reverse('posts:post_edit',
                                            kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    )

        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group, group_test)

    def test_guest_user_negativ_post_request(self):
        """Проверка негативного сценария для гостевого клиента при
           попытке редактирования поста.
        """
        post_count_before_request = Post.objects.count()
        form_data = {
            'text': '2_text_post_test',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,)
        self.post.refresh_from_db()
        post_count_after_request = Post.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(post_count_before_request, post_count_after_request)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
