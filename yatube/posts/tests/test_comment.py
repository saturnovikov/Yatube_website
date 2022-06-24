from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Comment

User = get_user_model()


class CommentTestCase(TestCase):
    """Класс для тестирования комментариев."""

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.post = Post.objects.create(
            text='test_text',
            author=self.user,
        )
        self.urls = {
            'add_comment': reverse('posts:add_comment',
                                   kwargs={'post_id': self.post.id}),
            'post_detail': reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}),
        }

    def test_comment_guest_client(self):
        """
        Комментировать посты может только авторизованный пользователь.
        """
        url = '/auth/login/'

        response = self.guest_client.get(self.urls['add_comment'])

        self.assertIn(url, response.url)

    def test_post_positive(self):
        """
        Проверка: комментарий появляется на странице поста.
        """
        form_data = {
            'text': 'Test_comment',
        }

        self.authorized_client.post(self.urls['add_comment'],
                                    data=form_data,
                                    )
        response = self.authorized_client.get(self.urls['post_detail'])

        self.assertEqual(Comment.objects.get(post=self.post).text,
                         form_data['text'],
                         '!!!Комментария нет в БД!!!')
        self.assertEqual(response.context.get('comments')[0].text,
                         form_data['text'],
                         '!!!Комментарий не передается в context!!!'
                         )
