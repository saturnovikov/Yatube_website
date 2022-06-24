from django import forms

from .models import Post, Comment


class PostForm (forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Название группы',
            'image': 'Изображение к посту'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост.',
            'image': 'Изображение к посту'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = (
            'Выберите группу, если желаете'
        )
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите какой-нибудь текст, пожалуйста.'
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария'}
        help_text = {'text': 'Введите комментарий'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'В данное поле, можно написать комментарий.'
        )
