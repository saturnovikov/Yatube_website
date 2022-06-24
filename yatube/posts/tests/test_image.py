import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImgTestCase(TestCase):
    """Класс для тестирования изображений."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.group = Group.objects.create(
            title='title_test',
            slug='slug_test',
        )
        self.post = Post.objects.create(
            text='text_post_test',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        self.urls = {
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile', args=[self.user]),
            'group_posts': reverse('posts:group_list',
                                   args=[self.group.slug]),
            'post_detail': reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}),
            'post_create': reverse('posts:post_create'),
        }
        cache.clear()

    def test_image_in_context(self):
        """
        Проверка, что при выводе поста с картинкой, изображение передаётся
        в словаре context.
        """

        context_test = {
            self.urls['index']: 'page_obj',
            self.urls['profile']: 'page_obj',
            self.urls['group_posts']: 'page_obj',
            self.urls['post_detail']: 'post',
        }

        for key, values in context_test.items():
            with self.subTest(reverse=key):
                response = self.authorized_client.get(key)
                if values == 'page_obj':
                    self.assertEqual(
                        response.context.get('page_obj').object_list[0].image,
                        self.post.image,
                        f'!!!Неверный context!!! для {key}'
                    )
                else:
                    self.assertEqual(
                        response.context.get(values).image,
                        self.post.image,
                        f'!!!Неверный context!!! для {key}'
                    )

    def test_creating_post_with_image(self):
        """
        Проверка, что при отправке поста с картинкой через форму
        PostForm, создаётся запись в базе данных.
        """
        posts_count = Post.objects.count()

        # приветствую, Виталий! вопрос: можешь обьяснить, пожалуйста, почему
        # если переменную uploaded
        # не прописывать в этой функции, а взять self.uploaded
        # и втсавить в form_data( 'image': self.uploaded), то пост
        # не создается?

        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': '2_text_post_test',
            'group': self.group.id,
            'image': uploaded,
        }

        self.authorized_client.post(self.urls['post_create'],
                                    data=form_data,
                                    follow=True,
                                    )

        self.assertEqual(
            Post.objects.count(), posts_count + 1,
            '!!!Не совпадает количество постов в БД!!!'
        )
        self.assertTrue(
            Post.objects.filter(
                text='2_text_post_test',
                image='posts/small_2.gif'
            ).exists(),
            '!!!Пост с данными не найден!!!'

        )
