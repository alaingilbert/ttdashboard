from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from settings import *
admin.autodiscover()

urlpatterns = patterns('',
   (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/js/' % PROJECT_ROOT}),
   (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/css/' % PROJECT_ROOT}),
   (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/img/' % PROJECT_ROOT}),
   (r'^tmp/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/templates/tmp/' % PROJECT_ROOT}),

   url(r'^api/', include('api.urls')),

   url(r'^criss/', include('website.urls')),
   #url(r'^', direct_to_template, {'template': 'manage.html'}),
   url(r'^', include('website.urls')),
   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   url(r'^admin/', include(admin.site.urls)),
)
