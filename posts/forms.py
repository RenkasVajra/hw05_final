from django import forms
from django.forms import ModelForm

from . import views
from posts.models import Comment, Follow, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image'] 
        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }
        help_text = {'name': 'Создайте свой новый пост.'}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Комментарий'}
        widgets = {'text': forms.Textarea({'rows': 3}),}


class FollowForm(ModelForm):
    model = Follow
    fields = ['author', 'user']
    