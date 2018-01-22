from time import mktime
from datetime import datetime, timedelta

import feedparser

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyplanet.models import Article

# add other feeds and/or not working ones
FEEDS = [
    'http://planetpython.org/rss20.xml',
    'https://pybit.es/feeds/all.rss.xml',
]


def _get_entries():
    for feed in FEEDS:
        yield from feedparser.parse(feed)['entries']


class Command(BaseCommand):
    help = 'Imports new Planet Python feed entries into articles table'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        # optional arg
        # https://stackoverflow.com/a/35635359
        days = options['days']
        go_back = datetime.now() - timedelta(days=days)

        count = 0

        for entry in sorted(_get_entries(),
                            key=lambda e: e['published_parsed'],
                            reverse=True):
            title = entry['title']
            url = entry['link']
            summary = entry.get('summary', 'No summary available')
            published = entry['published_parsed']
            dt = datetime.fromtimestamp(mktime(published))
            if dt < go_back:
                continue
            dt = timezone.make_aware(dt, timezone.get_current_timezone())

            obj, created = Article.objects.get_or_create(
                title=title,
                url=url,
                summary=summary,
                published=dt,
            )

            if created:
                confirm_msg = 'created'
                count += 1
            else:
                confirm_msg = 'already in DB'

            self.stdout.write('Article id {} {}'.format(obj.id, confirm_msg))

        self.stdout.write(
            self.style.SUCCESS(
                '{} articles added'.format(count)
            )
        )
