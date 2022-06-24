from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class CacheTestCase(TestCase):
    """Класс для тестирования кеша для главной страницы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        self.post = Post.objects.create(
            text='text_post_test',
            author=self.user,
        )
        cache.clear()

    def test_cache(self):
        """тест для проверки кеширования главной страницы."""
        url = reverse('posts:index')
        Post.objects.create(text='text_2', author=self.user)
        response_1 = self.authorized_client.get(url)

        Post.objects.get(pk=1).delete()
        response_2 = self.authorized_client.get(url)

        self.assertEqual(response_1.content, response_2.content)

        cache.clear()
        response_3 = self.authorized_client.get(url)
        self.assertNotEqual(response_1.content, response_3.content)
