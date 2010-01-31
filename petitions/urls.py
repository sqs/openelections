from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.petitions.views',
    (r'^$', 'index'),
    (r'^issues/(?P<issue_id>\d+)/?$', 'detail'),
    (r'^issues/(?P<issue_id>\d+)/sign$', 'sign'),
)