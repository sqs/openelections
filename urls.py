from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'openelections.issues.views.index'),
    (r'^petitions/', include('openelections.petitions.urls')),
    (r'^ballot/', include('openelections.ballot.urls')),
    (r'^issues/', include('openelections.issues.urls')),
    (r'^admin/?', include(admin.site.urls)),
    (r'^auth/', include('openelections.webauth.urls')),
    
   (r'^media/issue_images/(?P<path>.*)$', 'django.views.static.serve',
           {'document_root': 'public/media/issue_images/'}),
           
   (r'^(?P<issue_slug>[\w\d-]+)$', 'openelections.issues.views.detail'),
)
