from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('api.views',
   url(r'^$', 'home'),
   url(r'^user/id/(?P<user_id>\d+)/$', 'user_id'),
   url(r'^user/ttid/(?P<user_ttid>\w+)/$', 'user_ttid'),
   url(r'^user/name/(?P<username>\w+)/$', 'user_name'),
   url(r'^room/shortcut/(?P<shortcut>\w+)/$', 'room_shortcut'),
   url(r'^playlists/$', 'playlists'),
   url(r'^playlist/(?P<playlist_id>\d+)/$', 'playlist'),
)
