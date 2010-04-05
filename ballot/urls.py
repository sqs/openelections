from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot.views',
    (r'^$', 'index'),
    (r'^vote$', 'vote_all'),
    (r'^results$', 'results'),
)