from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.issues.views',
    (r'^$', 'index'),
    (r'^(?P<issue_id>\d+)/?$', 'detail'),
    (r'^(?P<issue_id>\d+)/edit$', 'edit'),
)