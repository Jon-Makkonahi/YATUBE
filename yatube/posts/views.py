from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def returns_the_paginator_page(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_QUANTITY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': returns_the_paginator_page(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': returns_the_paginator_page(request, group.posts.all())
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    following = user.is_authenticated and author.following.exists()
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': returns_the_paginator_page(request, author.posts.all()),
        'following': following
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
        'comments': post.comments.all(),
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/post_detail.html', {
            'form': form,
            'post': post,
        })
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:index')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
            'post': post,
            'is_edit': True,
        })
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__id__in=authors)
    return render(
        request,
        "posts/follow.html",
        {'page_obj': returns_the_paginator_page(request, posts_list)}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    profile_follow = Follow.objects.get(author=author,
                                        user=request.user)
    if Follow.objects.filter(pk=profile_follow.pk).exists():
        profile_follow.delete()
    return redirect('posts:profile', username=username)
