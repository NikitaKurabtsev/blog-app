from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.core.mail import send_mail

from blog.models import Post
from blog.forms import EmailPostForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


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
    return render(request, 'blog/post/detail.html', {'post_detail': post_detail})
