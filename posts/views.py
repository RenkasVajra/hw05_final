from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model 
from django.contrib.auth.decorators import login_required 
from django.core.checks.messages import Error 
from django.core.paginator import Paginator 
from django.contrib.auth import get_user_model 
from django.shortcuts import get_object_or_404 
from django.shortcuts import redirect, render 

from .forms import PostForm, CommentForm, FollowForm
from .models import Group, Post, Follow
 
 
User = get_user_model() 
 
 
def group_posts(request, slug): 

    group = get_object_or_404(Group, slug=slug) 
    posts = group.posts.all()[:12] 
    post_list = group.posts.all() 
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(request, 'group.html', {
        'posts': posts, 
        'group': group, 
        'page': page,  
        'paginator': paginator 
        },
    ) 


@cache_page(1 * 20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context)
 

@login_required 
def new_post(request): 

    form = PostForm(request.POST or None, files=request.FILES or None) 
    if not form.is_valid(): 
        return render(request, 'new.html', {
                'form': form, 
                'is_new': True,
            },
        )  
    post = form.save(commit=False) 
    post.author = request.user 
    post.save() 
    return redirect('index') 

     
def profile(request, username):

    author = get_object_or_404(User, username=username)
    authors_posts = author.posts.all() 
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author.following.exists()
    context = {
        'posts': authors_posts, 
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author 
    authors_posts = author.posts.all() 
    count = authors_posts.count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'count': count,
        'author': post.author,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):

    post = get_object_or_404(Post, author__username=username, pk=post_id) 
    form = PostForm(
            request.POST or None, 
            files=request.FILES or None,
            instance=post
        )
    if post.author != request.user: 
        return render(request, 'post.html', {
            'username': username, 
            'post_id': post.pk, 
        },
        )
    if not form.is_valid(): 
        return render(request, 'new.html', {
            'username': username, 
            'post_id': post.pk, 
            'post': post,
            'form': form
        },
        )    
    form.save()
    return redirect('post', username, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None,)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
            'post',
            username=username,
            post_id=post.pk
        )


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)

    
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = author.following.exists()
    if request.user != author and not following:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect('profile', username=username)
        

def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
    