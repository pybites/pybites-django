from urllib.parse import urlencode, quote_plus

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Article

OPEN = 0
SKIPPED = 1
SHARED = 2
MAX_ENTRIES = 100
PYBITES = 'pybit.es'
TWITTER_INTENT = 'https://twitter.com/intent/tweet?'


def index(request):
    articles = Article.objects.order_by('-published')[:MAX_ENTRIES]
    template = loader.get_template('pyplanet/index.html')
    context = {
        'title': 'Articles',
        'articles': articles,
    }
    return HttpResponse(template.render(context, request))


def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    article_text = article.title
    if PYBITES in article.url:
        article_text = 'New PyBites Article: ' + article_text

    payload = {'text': article_text, 'url': article.url}
    tweet_url_su = TWITTER_INTENT + urlencode(payload, quote_via=quote_plus)
    payload['via'] = 'pybites'
    tweet_url_guest = TWITTER_INTENT + urlencode(payload, quote_via=quote_plus)

    return render(request, 'pyplanet/detail.html', 
                  {'title': 'Article Detail',
                   'article': article,
                   'tweet_url_su': tweet_url_su,
                   'tweet_url_guest': tweet_url_guest,
                   })


def _update(request, article_id, status):
    article = get_object_or_404(Article, pk=article_id)
    article.status = status
    # TODO - edited_by
    article.save()
    return HttpResponseRedirect('/pyplanet')


def skip(request, article_id):
    return _update(request, article_id, SKIPPED)


def share(request, article_id):
    return _update(request, article_id, SHARED)
