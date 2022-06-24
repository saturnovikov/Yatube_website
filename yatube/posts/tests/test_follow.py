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

    def test_create_and_delete_following(self):
        """Проверка подписки на автора, удаление подписки."""
        null_post = 0

        # Проверка, что подписка на автора работает
        quantity_before_subscription = Follow.objects.count()

        self.authorized_client.get(self.urls['profile_follow'])
        print('quantity after subscription')
        quantity_after_subscription = Follow.objects.count()
        self.assertEqual(quantity_before_subscription,
                         quantity_after_subscription - 1)
        response_guest = self.guest_client.get(self.urls['profile_follow'])
        self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)

        # Проверка, что посты появляются в ленте тех кто подписан на автора
        response_follow = self.authorized_client.get(
            self.urls['index_follow'])
        response_author = self.authorized_client_author.get(
            self.urls['index_follow'])

        self.assertEqual(len(response_author.context.get('page_obj')),
                         null_post)
        self.assertEqual(len(response_follow.context.get('page_obj')),
                         self.check_post_user_author)

        # Проверка,что новый пост появляется в ленте тех кто подписан на автора
        text_post = 'new_text'
        Post.objects.create(author=self.user_author,
                            text=text_post)
        response_follow_1 = self.authorized_client.get(
            self.urls['index_follow'])
        response_author_1 = self.authorized_client_author.get(
            self.urls['index_follow'])
        self.assertEqual(
            response_follow_1.context.get('page_obj')[0].text,
            text_post)
        self.assertEqual(
            len(response_author_1.context.get('page_obj')), null_post
        )

        # Проверка отписки от автора
        response_unfollow = self.authorized_client.get(
            self.urls['profile_unfollow'])
        print('quantity after subscription deletion')
        quantity_after_subscription_deletion = Follow.objects.count()
        self.assertEquals(quantity_after_subscription - 1,
                          quantity_after_subscription_deletion)
