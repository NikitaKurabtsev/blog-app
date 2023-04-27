from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from taggit.models import Tag

from blog.forms import CommentForm, EmailPostForm
from blog.models import Comment, Post

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'page': page,
        'tag': tag,
    }
    return render(request, 'blog/post/list.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    post_url = request.build_absolute_uri(post.get_absolute_url())
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = f"{data['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{data['name']}'s comments: {data['comments']}"
            send_mail(subject, message, 'user@gmail.com', [data['to'],], fail_silently=True)
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'form': form,
                                                    'post': post,
                                                    'sent': sent})


def post_detail(request, year, month, day, post):
    post_detail = get_object_or_404(Post,
                                    slug=post,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)
    comments = post_detail.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        form = CommentForm(data=request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post_detail
            new_comment.save()
    else:
        form = CommentForm()
    context = {
        'post_detail': post_detail,
        'new_comment': new_comment,
        'form': form,
        'comments': comments,
    }

    return render(request, 'blog/post/detail.html', context)
