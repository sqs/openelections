from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.issues.views',
    (r'^manage/?$', 'manage_index'),
    (r'^manage/new/(?P<issue_kind>[\w\d-]+)/?$', 'manage_new'),
    (r'^manage/create/?$', 'create'),

    (r'^$', 'index'),
    (r'^(?P<show>[\w\d-]+)$', 'index'),
    (r'^issue/(?P<issue_slug>[\w\d-]+)/?$', 'detail'),
    

    (r'^issue/(?P<issue_slug>[\w\d-]+)/edit$', 'manage_edit'),
)