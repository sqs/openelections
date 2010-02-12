from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.issues.views',
    (r'^manage/?$', 'manage_index'),
    (r'^manage/new/(?P<issue_kind>[\w-]+)/?$', 'manage_new'),
    (r'^manage/create/?$', 'create'),

    (r'^$', 'index'),
    (r'^(?P<issue_slug>[\w-]+)/?$', 'detail'),
    

    (r'^(?P<issue_slug>[\w-]+)/edit$', 'edit'),
)