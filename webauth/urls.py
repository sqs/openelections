from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.webauth.views',
    (r'^logout$', 'logout'),
)