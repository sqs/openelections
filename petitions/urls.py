from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.petitions.views',
    (r'^$', 'index'),
    (r'^(?P<issue_slug>[\w-]+)/?$', 'detail'),
    (r'^(?P<issue_slug>[\w-]+)/sign$', 'sign'),
)