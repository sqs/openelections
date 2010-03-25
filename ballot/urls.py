from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot.views',
    (r'^$', 'index'),
    (r'^vote$', 'vote_all'),
    (r'^issues/(?P<issue_id>\d+)/vote$', 'vote_one'),
    (r'^results$', 'results'),
)