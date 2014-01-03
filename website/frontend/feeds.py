import copy
from django.contrib.syndication.views import Feed
from django.conf.urls import patterns
from .data import data
from .views import get_current_next, CONFIG

class RoomFeed(Feed):
    def __init__(self, *args, **kwargs):
        if 'group' in kwargs:
            self.group = kwargs.pop('group')
            self.link = '/{0}'.format(group)
            self.title = CONFIG.config(group)['title']
        else:
            self.group = ''
            self.link = '/'
        super(RoomFeed, self).__init__(*args, **kwargs)

    def items(self):
        items = copy.deepcopy(list(get_current_next(self.group)))
        items[0]['title'] = 'Now: ' + items[0]['title']
        items[1]['title'] = 'Next: ' + items[1]['title']
        return items

    #def get_object(self, request, *args, **kwargs):
    #    return self

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return item['abstract']

    def item_link(self, item):
        if 'url' in item:
            return item['url']
        return CONFIG.config('default')['url']

urls = patterns('', *[(r'^{0}/rss$'.format(group), RoomFeed(group=group)) for group in CONFIG.groups()])
