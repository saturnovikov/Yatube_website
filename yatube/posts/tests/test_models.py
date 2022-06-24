from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Класс для тестирования модели Post."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='User_test')
        cls.group = Group.objects.create(
            title='Название',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='A' * 20,
            author=cls.user,
        )

    def test_str(self):
        """Тестируем метод _str_ для модели Post."""
        NUMBER_OF_CHARACTERS = 15
        expected_object_name = self.group.title
        data = {str(self.post): self.post.text[:NUMBER_OF_CHARACTERS],
                str(self.group): expected_object_name,
                }

        for result, expected_value in data.items():
            with self.subTest(result=result):
                self.assertEqual(result, expected_value)

    def test_title_label_group(self):
        """Тестируем verbose_name поля title."""
        verbose = self.group._meta.get_field('title').verbose_name

        self.assertEqual(verbose, 'Название')
