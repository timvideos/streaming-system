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
        return get_current_next(self.group)

    #def get_object(self, request, *args, **kwargs):
    #    return self

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return item['abstract']

    def item_link(self, item):
        return u'http://timvideos.us/{0}'.format(self.group)

urls = patterns('', *[(r'^{0}/rss$'.format(group), RoomFeed(group=group)) for group in data.keys()])
