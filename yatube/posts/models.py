from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group (models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес URL', unique=True)
    description = models.TextField('Описание сообщества')

    class Meta:
        verbose_name = ('Сообщество')
        verbose_name_plural = ('Сообщества')

    def __str__(self):
        return f'{self.title}'


class Post (models.Model):
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Название сообщества',
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = ('Запись')
        verbose_name_plural = ('Записи')
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:15]}'


class Comment (models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий к посту',
        blank=False,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        blank=False,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField('Дата публикации комментария',
                                   auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        blank=False,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор постов',
        blank=False,
        on_delete=models.CASCADE,
        related_name='following'
    )
