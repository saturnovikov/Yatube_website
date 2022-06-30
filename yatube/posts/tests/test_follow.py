from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post, User

User = get_user_model()


class FollowTestCase(TestCase):
    """Класс для тестирования подписок."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(1, 4):
            username = f'{i}_test_user'
            User.objects.create_user(username=username)
        cls.user_author = User.objects.get(id=1)
        cls.user_authorization = User.objects.get(id=2)
        cls.user_authorization_follower = User.objects.get(id=3)
        cls.check_post_user_author = 3
        cls.check_post_user_authorization_follower = 2
        cls.number_test_posts = (cls.check_post_user_author
                                 + cls.check_post_user_authorization_follower)
        for i in range(1, cls.number_test_posts):
            if i <= cls.check_post_user_author:
                Post.objects.create(author=cls.user_author,
                                    text=f'{i}_post_text')
            else:
                Post.objects.create(
                    author=cls.user_authorization_follower,
                    text=f'{i}_post_text')

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_authorization_follower)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        self.guest_client = Client()

        self.urls = {
            'index_follow': reverse('posts:follow_index'),
            'profile_follow': reverse('posts:profile_follow',
                                      kwargs={'username': self.user_author}),
            'profile_unfollow': reverse('posts:profile_unfollow',
                                        kwargs={'username': self.user_author})
        }

    def test_authorization_client_following(self):
        """Авторизованный пользователь может подписаться."""
        user_id = self.user_authorization_follower.id
        author_id = self.user_author.id

        quantity_before_subscription = Follow.objects.count()

        response_authorization_client = self.authorized_client.get(
            self.urls['profile_follow'])
        quantity_after_subscription = Follow.objects.count()

        self.assertEqual(response_authorization_client.status_code,
                         HTTPStatus.FOUND)
        self.assertEqual(quantity_before_subscription,
                         quantity_after_subscription - 1)

        self.assertEqual(Follow.objects.all()[0].user_id,
                         user_id)
        self.assertEqual(Follow.objects.all()[0].author_id,
                         author_id)

    def test_guest_client_no_following(self):
        """Неавторизованный пользователь не может подписаться."""
        quantity_before_subscription = Follow.objects.count()

        self.guest_client.get(self.urls['profile_follow'])

        quantity_after_subscription = Follow.objects.count()

        self.assertEqual(quantity_before_subscription,
                         quantity_after_subscription)

    def test_create_post_follow(self):
        """Посты появляются в ленте тех кто подписан на автора."""
        text_post = 'text_post_test'
        self.authorized_client.get(self.urls['profile_follow'])
        Post.objects.create(
            author=self.user_author,
            text=text_post,
        )
        response = self.authorized_client.get(self.urls['index_follow'])
        self.assertEqual(response.context.get('page_obj')[0].text,
                         text_post)

    def test_no_create_post_follow(self):
        """Посты не появляются в ленте тех кто не подписан на автора."""
        text_post = 'text_post_test'

        self.authorized_client.get(self.urls['profile_follow'])
        Post.objects.create(
            author=self.user_authorization,
            text=text_post,
        )
        response = self.authorized_client.get(self.urls['index_follow'])

        self.assertNotEqual(response.context.get('page_obj')[0].text,
                            text_post)
