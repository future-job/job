# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect

from .models import Post
from .forms import PostForm

# Create your views here.

def main_page(request):
    return render(request, 'blog/index.html')

def detail_page(request):
    return render(request, 'blog/detail.html')

def list_page(request):
    return render(request, 'blog/list.html')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts':posts})

def post_detail(request, pk): # request, 그리고 urls에 지정한것과 동일한 이름인 pk를 넣어준다.
    post = get_object_or_404(Post, pk=pk) # pk가 없는 포스트라면 404페이지로 넘겨준다.
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":  # 폼에 입력된 데이터를 view페이지로 가지고 올 때. request는.POST 우리가 입력했던 데이터들 갖고있음.
        form = PostForm(request.POST)
        if form.is_valid():  # 폼에 들어있는 값들이 올바른지 확인. 잘못된 값이 있다면 저장 ㄴㄴ
            post = form.save(commit=False)  # 폼을 저장하는 작업.commit=False라고 해서 넘겨진 데이터를 바로 POST모델에 저장하지 말라. 작성자 추가해야하니까.
            post.author = request.user  # 작성자를 추가.
            post.published_date = timezone.now()
            post.save()  # 작성자까지 추가되고 저장.
            return redirect('ft_admin.views.post_detail', pk=post.pk)
    else:  # 처음 페이지에 접속했을때. 폼이 비어있어야 한다.
        form = PostForm()

    return render(request, 'blog/post_edit.html', {'form': form});

def post_edit(request, pk):  # url에서 pk를 받아서 처리
    post = get_object_or_404(Post, pk=pk)  # 수정하고자 하는 글의 Post모델 인스턴스를 가져온다. 원하는 글은 pk를 이용해 찾는다.
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('ft_admin.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form});