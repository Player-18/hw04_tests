from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView

from .forms import NewForm
from .models import Group, Post, User


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "latest": latest,
        "paginator": paginator
    }
    return render(request, "index.html", context)



def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = NewForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'new.html', {'form': form})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "author": user,
        "paginator": paginator
    }
    return render(request, 'profile.html', context)
 
 
def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    context = {
        "post": post,
        "author": post.author,
    }

    return render(request, 'post.html', context)



@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = NewForm(
        request.POST or None, files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }

    return render(request, 'new_post.html', context)

