from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'openelections.issues.views.index'),
    (r'^petitions/', include('openelections.petitions.urls')),
    (r'^ballot/', include('openelections.ballot.urls')),
    (r'^issues/', include('openelections.issues.urls')),
    (r'^admin/', include(admin.site.urls)),
    
   (r'^public/issue_images/(?P<path>.*)$', 'django.views.static.serve',
           {'document_root': 'public/issue_images/'}),
)
