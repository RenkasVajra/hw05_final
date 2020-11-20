from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    
    title = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        unique=True,   
    )

    description = models.TextField()
    
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'date published', 
        auto_now_add=True,
    )

    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='posts',
    )

    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        related_name='posts', 
        blank=True, 
        null=True,
    )

    image = models.ImageField(
        upload_to='posts/',
        blank=True, 
        null=True
    )  

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comment_post"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_author"
    )

    text = models.TextField(max_length=400)
    created_on = models.DateTimeField(
        'date published',
        auto_now_add=True,
    )

    pub_date = models.DateTimeField(
        'date published', 
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    
    class Meta:
        models.UniqueConstraint(
            fields=['author', 'user'], 
            name='followint_unique'
        )