from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot.views',
    (r'^$', 'index'),
    (r'^issues/(?P<issue_id>\d+)/vote?$', 'vote'),
    (r'^results/?$', 'results'),
)