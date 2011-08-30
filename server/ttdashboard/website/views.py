from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
from website.models import *
from website.forms import *
from django.db import connection, transaction
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.mail import send_mail
from django.utils.html import escape
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from website.crypto import rc4EncryptStr, rc4DecryptStr
from datetime import datetime
from settings import SECRET_KEY, SCRIPTS_PATH
import urllib, urllib2
import re, json, hashlib, random
import subprocess


def authkey(req):
   ctx = {}
   return render_to_response('authkey.html', ctx, context_instance=RequestContext(req))


@login_required
def playlists_export(req, playlist_id):
   ctx = {}
   cursor = connection.cursor()

   user = req.user
   profile = user.get_profile()
   uid = profile.ttuid
   auth = rc4DecryptStr(profile.auth_key, SECRET_KEY)

   if not uid: raise Http404


   if not auth:
      ctx.update({'error':'You must set your auth key to communicate with turntable.fm'})
      return render_to_response('authkey.html', ctx, context_instance=RequestContext(req))


   cursor.execute("SELECT \
                     p.id, \
                     p.name, \
                     p.comment \
                   FROM playlists AS p \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])
   if cursor.rowcount != 1:
      raise Http404


   if req.GET.get('confirm', None) is None:
      return render_to_response('ttaction.html', ctx, context_instance=RequestContext(req))


   cursor.execute("SELECT userid FROM users WHERE id=%s LIMIT 1", [uid])
   
   auth = rc4DecryptStr(profile.auth_key, SECRET_KEY)
   ttuid = dict_cursor(cursor)[0].get('userid')

   # Get the playlist
   params = ['python', '%s/export.py' % SCRIPTS_PATH, auth, ttuid]


   playlist = dict_cursor(cursor)[0]

   cursor.execute("SELECT \
                     s.id, \
                     s.songid, \
                     s.album, \
                     s.artist, \
                     s.coverart, \
                     s.song \
                   FROM playlists_songs AS ps \
                   LEFT JOIN songs AS s \
                     ON s.id = ps.song_id \
                   WHERE playlist_id = %s \
                  ", [playlist_id])
   songs = dict_cursor(cursor)
   for song in songs:
      params.append(song['songid']);

   p = subprocess.Popen(params, shell=False, stdout=subprocess.PIPE)
   stdout, stderr = p.communicate()
   data = json.loads(stdout)

   ctx.update({'songs':list})

   return HttpResponseRedirect('/profile/playlists/%s/' % playlist_id)


@csrf_exempt
@login_required
def playlists_import_save(req):
   if req.method != 'POST':
      raise Http404

   cursor = connection.cursor()

   playlist = []
   for p in req.POST:
      if p[:5] == 'song_':
         if req.POST[p] not in playlist:
            playlist.append(req.POST[p])
   print playlist

   name = 'import from tt.fm : %s' % (datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
   comment = '...'
   cursor.execute("INSERT INTO playlists \
                   (uid, created, name, comment) \
                   VALUES \
                   (%s, NOW(), %s, %s) \
                  ", [req.user.id, name, comment])
   playlist_id = cursor.lastrowid

   insert = ''
   for song_id in playlist:
      print "%s - %s" % (song_id, playlist_id)
      insert += "('%s', '%s', NOW(), ''),\n" % (str(song_id), int(playlist_id))
   insert = insert[:-2]
   print insert

   sql = "INSERT INTO playlists_songs \
          (song_id, playlist_id, created, comment) \
          VALUES \
          %s \
          " % insert
   cursor.execute(sql)
   transaction.commit_unless_managed()

   return HttpResponseRedirect('/profile/playlists/%s/' % playlist_id)


@login_required
def playlists_import(req):
   ctx = {}
   cursor = connection.cursor()

   user = req.user
   profile = user.get_profile()
   uid = profile.ttuid
   auth = profile.auth_key

   if not uid: raise Http404


   if not auth:
      ctx.update({'error':'You must set your auth key to communicate with turntable.fm'})
      return render_to_response('authkey.html', ctx, context_instance=RequestContext(req))


   if req.GET.get('confirm', None) is None:
      return render_to_response('ttaction.html', ctx, context_instance=RequestContext(req))


   cursor.execute("SELECT userid FROM users WHERE id=%s LIMIT 1", [uid])

   ttuid = dict_cursor(cursor)[0].get('userid')

   # Get the playlist
   auth = rc4DecryptStr(profile.auth_key, SECRET_KEY)
   p = subprocess.Popen(['python', '%s/import.py' % SCRIPTS_PATH, auth, ttuid], shell=False, stdout=subprocess.PIPE)
   stdout, stderr = p.communicate()
   data = json.loads(stdout)

   list = data.get('list')

   params = []
   for song in list:
      song['songid']    = song.get('_id')
      songid            = song.get('_id')
      album             = song['metadata'].get('album', '')
      artist            = song['metadata'].get('artist', '')
      coverart          = song['metadata'].get('coverart', '')
      song_name         = song['metadata'].get('song', '')
      length            = song['metadata'].get('length', 0)
      mnid              = song['metadata'].get('mnid', 0)
      genre             = song['metadata'].get('genre', '')
      filepath          = song['metadata'].get('filepath', '')
      bitrate           = song['metadata'].get('bitrate', 0)
      nb_play           = 0

      params = [songid, album, artist, coverart, song_name, length, mnid, genre, filepath, bitrate, nb_play]
      print params

      sql = "INSERT INTO songs \
             (songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play) \
             VALUES \
             (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
             ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id) \
            "
      cursor.execute(sql, params)
      song['id']        = cursor.lastrowid

   transaction.commit_unless_managed()

   ctx.update({'songs':list})

   return render_to_response('playlists_import.html', ctx, context_instance=RequestContext(req))


@login_required
def playlist_remove_song(req, playlist_id, song_id):
   ctx = {}
   cursor = connection.cursor()
   cursor.execute("SELECT id, comment, name \
                   FROM playlists \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])

   if cursor.rowcount != 1:
      raise Http404

   cursor.execute("DELETE FROM playlists_songs \
                  WHERE playlist_id = %s AND song_id = %s \
                 ", [playlist_id, song_id])
   transaction.commit_unless_managed()

   return HttpResponseRedirect('/profile/playlists/%s/' % playlist_id)


@login_required
def playlist(req, playlist_id):
   ctx = {}
   cursor = connection.cursor()
   cursor.execute("SELECT \
                     p.id, \
                     p.name, \
                     p.comment \
                   FROM playlists AS p \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])
   if cursor.rowcount != 1:
      raise Http404

   playlist = dict_cursor(cursor)[0]

   cursor.execute("SELECT \
                     s.id, \
                     s.album, \
                     s.artist, \
                     s.coverart, \
                     s.song \
                   FROM playlists_songs AS ps \
                   LEFT JOIN songs AS s \
                     ON s.id = ps.song_id \
                   WHERE playlist_id = %s \
                  ", [playlist_id])
   songs = dict_cursor(cursor)

   ctx.update({'playlist':playlist})
   ctx.update({'songs':songs})

   return render_to_response('playlist.html', ctx, context_instance=RequestContext(req))


@login_required
def playlists_add_song(req, song_id):
   ctx = {}
   cursor = connection.cursor()

   if req.method == 'POST':
      playlists_ids = []
      for p in req.POST:
         if p[:8] == 'playlist':
            playlists_ids.append(req.POST[p])

      insert = ''
      for id in playlists_ids:
         insert += "('%s', '%s', NOW(), '')," % (int(song_id), int(id))
      insert = insert[:-1]

      sql = "INSERT INTO playlists_songs \
             (song_id, playlist_id, created, comment) \
             VALUES \
             %s \
             ON DUPLICATE KEY UPDATE song_id=VALUES(song_id) \
             " % insert
      cursor.execute(sql)
      transaction.commit_unless_managed()

      return HttpResponseRedirect('/profile/playlists/')


   cursor = connection.cursor()
   cursor.execute("SELECT \
                     p.id, \
                     p.uid, \
                     p.created, \
                     p.comment, \
                     p.name, \
                     ps.song_id, \
                     ps.playlist_id, \
                     ps.created, \
                     ps.comment AS song_comment \
                   FROM playlists AS p \
                   LEFT JOIN playlists_songs AS ps \
                     ON ps.playlist_id = p.id AND ps.song_id = %s \
                   WHERE p.uid = %s \
                   GROUP BY p.id \
                  ", [song_id, req.user.id])

   if cursor.rowcount <= 0:
      raise Http404

   playlists = dict_cursor(cursor)
   ctx.update({'playlists':playlists})

   return render_to_response('playlists_add_song.html', ctx, context_instance=RequestContext(req))


@login_required
def add_playlists(req):
   ctx = {}
   cursor = connection.cursor()

   if req.method == 'POST':
      form = PlaylistForm(req.POST)
      if form.is_valid():
         name = req.POST['name']
         comment = req.POST['comment']

         cursor.execute("INSERT INTO playlists \
                         (uid, created, name, comment) \
                         VALUES \
                         (%s, %s, %s, %s) \
                        ", [req.user.id, datetime.now(), name, comment])
         transaction.commit_unless_managed()

         return HttpResponseRedirect('/profile/playlists/')
   else:
      form = PlaylistForm()

   ctx.update(csrf(req))
   ctx.update({'form':form})
   return render_to_response('add_playlists.html', ctx, context_instance=RequestContext(req))


@login_required
def playlists(req):
   ctx = {}
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     p.id, p.name, p.comment, \
                     COUNT(ps.playlist_id) AS nb_songs \
                   FROM playlists AS p \
                   LEFT JOIN playlists_songs AS ps \
                     ON ps.playlist_id = p.id \
                   WHERE p.uid = %s \
                   GROUP BY p.id \
                  ", [req.user.id])
   playlists = dict_cursor(cursor)

   ctx.update({'playlists':playlists})

   return render_to_response('playlists.html', ctx, context_instance=RequestContext(req))


@login_required
def edit_playlists(req, playlist_id):
   ctx = {}

   cursor = connection.cursor()
   cursor.execute("SELECT id, comment, name \
                   FROM playlists \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])

   if cursor.rowcount != 1:
      raise Http404

   playlist = dict_cursor(cursor)[0]

   if req.method == 'POST':
      form = PlaylistForm(req.POST)
      if form.is_valid():
         name = req.POST.getlist('name')[0] if len(req.POST.getlist('name')) > 0 else ''
         comment = req.POST.getlist('comment')[0] if len(req.POST.getlist('comment')) > 0 else ''

         cursor.execute("UPDATE playlists \
                        SET name = %s, \
                            comment = %s \
                        WHERE id = %s AND uid = %s \
                       ", [name, comment, playlist_id, req.user.id])
         transaction.commit_unless_managed()

         return HttpResponseRedirect('/profile/playlists/')
   else:
      form = PlaylistForm(playlist)

   ctx.update(csrf(req))
   ctx.update({'form':form})
   return render_to_response('edit_playlists.html', ctx, context_instance=RequestContext(req))


@login_required
def delete_playlists(req, playlist_id):
   ctx = {}

   cursor = connection.cursor()
   cursor.execute("SELECT id, comment, name \
                   FROM playlists \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])

   if cursor.rowcount != 1:
      raise Http404

   cursor.execute("DELETE FROM playlists \
                  WHERE id = %s AND uid = %s \
                 ", [playlist_id, req.user.id])
   transaction.commit_unless_managed()

   return HttpResponseRedirect('/profile/playlists/')


@login_required
def edit_profile(req):
   ctx = {}
   
   user = get_object_or_404(User, pk=req.user.id)
   profile = user.get_profile()

   if req.method == 'POST':
      form = ProfileForm(req.POST)

      auth_key = req.POST.getlist('auth_key')[0] if len(req.POST.getlist('auth_key')) > 0 else ''
      if len(auth_key) != 0 and len(auth_key) != 50:
         ctx.update(csrf(req))
         ctx.update({'form':form})
         ctx.update({'error':'Your auth key may have 50 chars.'})
         return render_to_response('edit_profile.html', ctx, context_instance=RequestContext(req))
      if len(auth_key) != 0 and auth_key[:10] != 'auth+live+':
         ctx.update(csrf(req))
         ctx.update({'form':form})
         ctx.update({'error':'Your auth key is invalid.'})
         return render_to_response('edit_profile.html', ctx, context_instance=RequestContext(req))
            
      if form.is_valid():
         first_name = req.POST.getlist('first_name')[0] if len(req.POST.getlist('first_name')) > 0 else ''
         last_name = req.POST.getlist('last_name')[0] if len(req.POST.getlist('last_name')) > 0 else ''

         auth_key = rc4EncryptStr(auth_key, SECRET_KEY)

         user.first_name = first_name
         user.last_name = last_name
         user.save()

         profile.auth_key = auth_key
         profile.save()

         return HttpResponseRedirect('/profile/')
   else:
      dict = user.__dict__
      dict.update(profile.__dict__)
      if dict['auth_key']:
         dict['auth_key'] = rc4DecryptStr(dict['auth_key'], SECRET_KEY)
      form = ProfileForm(dict)

   ctx.update(csrf(req))
   ctx.update({'form':form})
   return render_to_response('edit_profile.html', ctx, context_instance=RequestContext(req))


@login_required
def profile(req):
   ctx = {}
   cursor = connection.cursor()

   auth_user = req.user
   auth_profile = auth_user.get_profile()

   cursor.execute("SELECT \
                     * \
                   FROM users AS u \
                   WHERE u.id = %s \
                   LIMIT 1", [auth_profile.ttuid])
   user = None
   if cursor.rowcount == 1:
      user = dict_cursor(cursor)[0]


      #if not cache.get('profile_%s_newsongs' % auth_profile.ttuid):
      #   # Select my 10 favs songs.
      #   cursor.execute("SELECT \
      #                     song_id, \
      #                     nb, \
      #                     user_id \
      #                   FROM users_songs_liked \
      #                   WHERE user_id=%s \
      #                   ORDER BY nb DESC \
      #                   LIMIT 100", [auth_profile.ttuid])
      #   songs_like = dict_cursor(cursor)

      #   l = []
      #   for s in songs_like:
      #      l.append(s['song_id'])

      #   if len(l) > 0:
      #      ctx.update({'songs_like':songs_like})

      #      # Who love those songs
      #      cursor.execute("SELECT \
      #                        song_id, \
      #                        nb, \
      #                        user_id \
      #                      FROM users_songs_liked \
      #                      WHERE song_id IN %s \
      #                      ORDER BY nb DESC \
      #                      LIMIT 15", [l[:5]])
      #      users_like = dict_cursor(cursor)
      #      ctx.update({'users_like':users_like})

      #      l2 = []
      #      for u in users_like:
      #         l2.append(u['user_id'])

      #      # Get common loved songs.
      #      cursor.execute("SELECT \
      #                        SUM(nb) AS test, \
      #                        s.id AS song_id, \
      #                        s.song AS song_name, \
      #                        s.artist AS song_artist, \
      #                        s.genre AS song_genre, \
      #                        s.coverart AS song_coverart, \
      #                        s.previewurl, \
      #                        s.collectionviewurl, \
      #                        s.album AS song_album \
      #                      FROM users_songs_liked AS usl \
      #                      LEFT JOIN songs AS s \
      #                        ON s.id = song_id \
      #                      WHERE user_id IN %s AND usl.song_id NOT IN %s  \
      #                      GROUP BY usl.song_id \
      #                      ORDER BY test DESC \
      #                      LIMIT 20", [l2, l])
      #      songs_like2 = dict_cursor(cursor)

      #      for s in songs_like2:
      #         if not s['previewurl']:
      #            print "CALISS"
      #            print s['previewurl']
      #            data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (s['song_artist'], s['song_name']), 'entity':'song', 'limit':'25'})).read())
      #            if len(data['results']):
      #               previewurl = data['results'][0].get('previewUrl')
      #               collectionviewurl = data['results'][0].get('collectionViewUrl')
      #               cursor.execute("UPDATE songs SET previewurl=%s, collectionviewurl=%s WHERE id = %s", [previewurl, collectionviewurl, s['song_id']])
      #               s['previewurl'] = data['results'][0].get('previewUrl')
      #            else:
      #               cursor.execute("UPDATE songs SET previewurl='NOTHING', collectionviewurl='NOTHING' WHERE id = %s", [s['song_id']])
      #               s['previewurl'] = ''
      #         transaction.commit_unless_managed()

      #      ctx.update({'discover_songs':songs_like2})

      #      cache.set('profile_%s_newsongs' % auth_profile.ttuid, songs_like2, 60*15)
      #else:
      #   songs_like2 = cache.get('profile_%s_newsongs' % auth_profile.ttuid)
      #   ctx.update({'discover_songs':songs_like2})


   ctx.update({'tuser':user})
   return render_to_response('profile.html', ctx, context_instance=RequestContext(req))


@login_required
def link_profile(req, uid):
   cursor = connection.cursor()
   cursor.execute("SELECT * FROM users WHERE id = %s LIMIT 1", [uid])
   count = cursor.rowcount
   if count != 1:
      raise Http404

   profile = req.user.get_profile()
   profile.ttuid = uid
   profile.save()
   return HttpResponseRedirect('/profile/')


@login_required
def change_email(req):
   if req.method == 'POST':
      pass


@login_required
def user_logout(req):
   logout(req)
   return HttpResponseRedirect('/')


def generate_password():
   chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
   psw   = ""
   for i in range(0, 10):
      c = random.randint(0, len(chars)-1)
      psw += chars[c]
   return psw


@csrf_exempt
def password_recovery(req):
   if req.method == 'POST':
      form = RecoveryForm(req.POST)
      if form.is_valid():
         email = req.POST['email']
         try:
            tmp = User.objects.get(email=email)
         except:
            ctx = {'err':'This email does not exists.'}
            return render_to_response('recovery.html', ctx, context_instance=RequestContext(req))

         hash = hashlib.sha1(str(datetime.now())).hexdigest()
         PasswordRecovery.objects.create(hash=hash, email=email)

         send_mail('ttDashboard password recovery', 'http://ttdashboard.com/recovery/%s/' % hash, 'no-reply@ttdashboard.com', [email], fail_silently=False)
         return HttpResponseRedirect('/')
   else:
      return render_to_response('recovery.html', {}, context_instance=RequestContext(req))


def password_recovery2(req, key):
   recovery = get_object_or_404(PasswordRecovery, hash=key)
   email    = recovery.email
   recovery.delete()
   password = generate_password()
   user = User.objects.get(email=email)
   username = user.username
   user.set_password(password)
   user.save()
   send_mail('ttDashboard password recovery', 'Username: %s, New password: %s' % (username, password), 'no-reply@ttdashboard.com', [email], fail_silently=False)
   return HttpResponseRedirect('/')


@csrf_exempt
def change_password(req):
   if req.method == 'POST':
      form = ChangePasswordForm(req.POST)
      if form.is_valid():
         password = req.POST['password']
         if len(password) < 5:
            ctx = {'err':'Your password must have at least 5 characters.'}
            return render_to_response('change_password.html', ctx, context_instance=RequestContext(req))

         user = req.user
         user.set_password(password)
         user.save()

         return HttpResponseRedirect('/profile/')
   else:
      return render_to_response('change_password.html', {}, context_instance=RequestContext(req))


@csrf_exempt
def user_login(req):
   if req.method == 'POST': # If the form has been submitted...
      form = LoginForm(req.POST) # A form bound to the POST data
      if form.is_valid(): # All validation rules pass
         user = authenticate(username=req.POST['username'], password=req.POST['password'])
         if user is not None:
            login(req, user)
            return HttpResponseRedirect('/profile/')
      return render_to_response('login.html', {'err':'Bad username/password'}, context_instance=RequestContext(req))
   else:
      raise Http404


@csrf_exempt
def user_register(req):
   if req.method == 'POST':
      form = RegisterForm(req.POST)
      if form.is_valid():
         username = req.POST['username']
         email = req.POST['email']
         password = req.POST['password']
         
         try:
            tmp = User.objects.get(email=email)
            return render_to_response('register.html', {'err':'Email already taken'}, context_instance=RequestContext(req))
         except:
            pass
         try:
            tmp = User.objects.get(username=username)
            return render_to_response('register.html', {'err':'Username already taken'}, context_instance=RequestContext(req))
         except:
            pass


         key = hashlib.sha1(str(datetime.now())).hexdigest()
         api_key = hashlib.sha1(str(datetime.now()) + str(random.randint(0, 100000))).hexdigest()
         user = User.objects.create_user(username, email, password)
         user.is_active = False
         user.save()
         profile = user.get_profile()
         profile.activation_key = key
         profile.api_key = api_key
         profile.save()

         send_mail('ttDashboard confirmation', 'http://ttdashboard.com/activate/%s/' % key, 'no-reply@ttdashboard.com', [email], fail_silently=False)
         
         user = authenticate(username=username, password=password)
         if user is not None:
            login(req, user)
            return HttpResponseRedirect('/profile/')
      return render_to_response('register.html', {'err':'Invalid form'}, context_instance=RequestContext(req))
   else:
      raise Http404


def user_activate(req, key):
   profile = get_object_or_404(UserProfile, activation_key=key)
   user = profile.user
   if user.is_active:
      raise Http404
   profile.activation_key = None
   profile.save()
   user.is_active = True
   user.save()
   return HttpResponseRedirect('/')


def dict_cursor(cursor):
   description = [x[0] for x in cursor.description]
   rows = []
   for row in cursor:
      rows.append(dict(zip(description, row)))
   return rows

@cache_page(10)
def ajax_home(req):
   if req.is_ajax():
      cursor = connection.cursor()

      cursor.execute("SELECT \
                        r.roomid AS roomid, \
                        r.name AS room_name, \
                        r.shortcut AS room_shortcut, \
                        r.listeners AS room_listeners, \
                        u.id AS current_dj_id, \
                        u.name AS current_dj, \
                        s.nb_play AS room_nb_play, \
                        s.song AS song_name, \
                        s.coverart AS song_coverart, \
                        r.downvotes, \
                        r.upvotes \
                      FROM rooms AS r \
                      LEFT JOIN songs AS s \
                        ON s.id = r.current_song \
                      LEFT JOIN users AS u \
                        ON u.id = r.current_dj \
                      ORDER BY r.listeners DESC \
                      LIMIT 6")
      rooms = dict_cursor(cursor)
   
      return render_to_response('ajax_home.html', {'rooms':rooms}, context_instance=RequestContext(req))


def top_users_points(req):
   cursor = connection.cursor()
   cursor.execute("SELECT * FROM users \
                   WHERE id NOT IN (11717, 139, 13248, 532, 580) \
                   ORDER BY points DESC LIMIT 12")
   users_points = dict_cursor(cursor)
   return users_points


def top_users_fans(req):
   cursor = connection.cursor()
   cursor.execute("SELECT * FROM users \
                   WHERE id NOT IN (6902) \
                   ORDER BY fans DESC LIMIT 12")
   users_fans = dict_cursor(cursor)
   return users_fans


def top_songs(req):
   cursor = connection.cursor()
   cursor.execute("SELECT * FROM songs ORDER BY nb_play DESC LIMIT 12")
   pop_songs = dict_cursor(cursor)
   return pop_songs


def v2_0(req):
   pass
   ctx = {}
   return render_to_response('v2_0.html', ctx, context_instance=RequestContext(req))


def home(req):
   if req.is_ajax():
      raise Http404

   cursor = connection.cursor()

   cursor.execute("SELECT \
                     r.roomid AS roomid, \
                     r.name AS room_name, \
                     r.shortcut AS room_shortcut, \
                     r.listeners AS room_listeners, \
                     u.id AS current_dj_id, \
                     u.name AS current_dj, \
                     s.nb_play AS room_nb_play, \
                     s.song AS song_name, \
                     s.coverart AS song_coverart, \
                     r.downvotes, \
                     r.upvotes \
                   FROM rooms AS r \
                   LEFT JOIN songs AS s \
                     ON s.id = r.current_song \
                   LEFT JOIN users AS u \
                     ON u.id = r.current_dj \
                   ORDER BY r.listeners DESC \
                   LIMIT 6")
   rooms = dict_cursor(cursor)

   if not cache.get('top_users_points'):
      users_points = top_users_points(req)
      cache.set('top_users_points', users_points, 60*15)
   else:
      users_points = cache.get('top_users_points')

   if not cache.get('top_users_fans'):
      users_fans = top_users_fans(req)
      cache.set('top_users_fans', users_fans, 60*15)
   else:
      users_fans = cache.get('top_users_fans')

   if not cache.get('top_songs'):
      pop_songs = top_songs(req)
      cache.set('top_songs', pop_songs, 60*15)
   else:
      pop_songs = cache.get('top_songs')

   return render_to_response('home.html', {'onglet':'home', 'users_points':users_points, 'users_fans':users_fans, 'pop_songs':pop_songs, 'rooms':rooms}, context_instance=RequestContext(req))


def songs(req):
   cursor = connection.cursor()

   if not cache.get('songs_ups'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) AS upvotes, \
                        s.coverart, s.id, s.song \
                      FROM songs AS s \
                      LEFT JOIN song_log AS sl \
                        ON sl.song_id = s.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.song_id, s.id, s.song, s.coverart \
                      ORDER BY upvotes DESC \
                      LIMIT 10")
      ups = dict_cursor(cursor)
      cache.set('songs_ups', ups, 60*15)
   else:
      ups = cache.get('songs_ups')


   if not cache.get('songs_downs'):
      cursor.execute("SELECT \
                        SUM(sl.downvotes) AS downvotes, \
                        s.coverart, s.id, s.song \
                      FROM songs AS s \
                      LEFT JOIN song_log AS sl \
                        ON sl.song_id = s.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.song_id, s.id, s.song, s.coverart \
                      ORDER BY downvotes DESC \
                      LIMIT 10")
      downs = dict_cursor(cursor)
      cache.set('songs_downs', downs, 60*15)
   else:
      downs = cache.get('songs_downs')


   if not cache.get('songs_combined'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) - SUM(sl.downvotes) AS votes, \
                        s.coverart, s.id, s.song \
                      FROM songs AS s \
                      LEFT JOIN song_log AS sl \
                        ON sl.song_id = s.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.song_id, s.id, s.song, s.coverart \
                      ORDER BY votes DESC \
                      LIMIT 10")
      combined = dict_cursor(cursor)
      cache.set('songs_combined', combined, 60*15)
   else:
      combined = cache.get('songs_combined')


   if not cache.get('songs_pop_songs'):
      cursor.execute("SELECT \
                        COUNT(sl.song_id) AS nb_play, \
                        s.coverart, s.id, s.song \
                      FROM songs AS s \
                      LEFT JOIN song_log AS sl \
                        ON sl.song_id = s.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.song_id, s.id, s.song, s.coverart \
                      ORDER BY nb_play DESC \
                      LIMIT 10")
      pop_songs = dict_cursor(cursor)
      cache.set('songs_pop_songs', pop_songs, 60*15)
   else:
      pop_songs = cache.get('songs_pop_songs')


   return render_to_response('songs.html', {'onglet':'songs', 'ups':ups, 'downs':downs, 'combined':combined, 'pop_songs':pop_songs}, context_instance=RequestContext(req))


#@cache_page(60 * 15)
def songs_played(req):
   cursor = connection.cursor()
   cursor.execute("SELECT * FROM songs ORDER BY nb_play DESC LIMIT 100")
   pop_songs = dict_cursor(cursor)
   return render_to_response('songs_played.html', {'onglet':'songs', 'pop_songs':pop_songs}, context_instance=RequestContext(req))


def song_ttid(req, song_id):
   cursor = connection.cursor()
   cursor.execute("SELECT s.id, s.song, s.album, s.artist, s.length, s.genre, s.nb_play, s.coverart \
                   FROM songs AS s \
                   WHERE s.songid=%s \
                   LIMIT 1", [song_id])
   song = dict_cursor(cursor)[0]
   song['length'] = format_length(song['length'])

   try:
      data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (song['artist'], song['song']), 'entity':'song', 'limit':'1'})).read())
      if data['results']:
         song['previewUrl'] = data['results'][0].get('previewUrl')
         song['collectionViewUrl'] = data['results'][0].get('collectionViewUrl')
   except:
      pass

   cursor.execute("SELECT SUM(sl.upvotes) AS upvotes, \
                     SUM(sl.downvotes) AS downvotes \
                   FROM songlog AS sl \
                   WHERE sl.songid=%s \
                   LIMIT 1", [song['id']])
   votes = dict_cursor(cursor)[0]
   song['upvotes'] = votes['upvotes']
   song['downvotes'] = votes['downvotes']

   cursor.execute("SELECT sl.upvotes AS upvotes, \
                     sl.downvotes AS downvotes, \
                     sl.starttime, \
                     sl.current_dj AS current_dj_id, \
                     u.name AS current_dj, \
                     r.name AS room_name, \
                     r.roomid AS roomid, \
                     r.shortcut AS room_shortcut \
                   FROM songlog AS sl \
                   LEFT JOIN users AS u \
                     ON u.id = sl.current_dj \
                   LEFT JOIN rooms AS r \
                     ON r.id = sl.roomid \
                   WHERE sl.songid=%s \
                   ORDER BY sl.starttime DESC \
                   LIMIT 20", [song['id']])
   appreciation_log = dict_cursor(cursor)

   return render_to_response('song.html', {'onglet':'songs', 'song':song, 'appreciation_log':appreciation_log}, context_instance=RequestContext(req))


def song(req, song_id):
   cursor = connection.cursor()
   cursor.execute("SELECT s.id, s.song, s.album, s.artist, s.length, s.genre, s.nb_play, s.coverart \
                   FROM songs AS s \
                   WHERE s.id=%s \
                   LIMIT 1" % int(song_id))
   song = dict_cursor(cursor)[0]
   song['length'] = format_length(song['length'])

   try:
      data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (song['artist'], song['song']), 'entity':'song', 'limit':'1'})).read())
      if data['results']:
         song['previewUrl'] = data['results'][0].get('previewUrl')
         song['collectionViewUrl'] = data['results'][0].get('collectionViewUrl')
   except:
      pass

   cursor.execute("SELECT SUM(sl.upvotes) AS upvotes, \
                     SUM(sl.downvotes) AS downvotes \
                   FROM song_log AS sl \
                   WHERE sl.song_id=%s \
                   LIMIT 1" % (int(song_id)))
   votes = dict_cursor(cursor)[0]
   song['upvotes'] = votes['upvotes']
   song['downvotes'] = votes['downvotes']

   cursor.execute("SELECT sl.upvotes AS upvotes, \
                     sl.downvotes AS downvotes, \
                     sl.dj AS current_dj_id, \
                     sl.created, \
                     u.name AS current_dj, \
                     r.name AS room_name, \
                     r.roomid AS roomid, \
                     r.shortcut AS room_shortcut \
                   FROM song_log AS sl \
                   LEFT JOIN users AS u \
                     ON u.id = sl.dj \
                   LEFT JOIN rooms AS r \
                     ON r.id = sl.room_id \
                   WHERE sl.song_id=%s \
                   ORDER BY sl.created DESC \
                   LIMIT 20" % (int(song_id)))
   appreciation_log = dict_cursor(cursor)

   return render_to_response('song.html', {'onglet':'songs', 'song':song, 'appreciation_log':appreciation_log}, context_instance=RequestContext(req))


def format_length(length):
   if length != None:
      minutes = length / 60
      secondes = length - minutes * 60
      return "%sm %s" % (minutes, secondes)
   else:
      return ""


@cache_page(10)
def ajax_room_infos(req, shortcut):
   if not req.is_ajax():
      raise Http404

   if re.match('^\w{24}$', shortcut):
      where = 'r.roomid'
   else:
      where = 'r.shortcut'

   cursor = connection.cursor()

   cursor.execute("SELECT \
                     r.id AS room_id, \
                     r.name AS room_name, \
                     r.description AS room_description, \
                     r.shortcut AS room_shortcut, \
                     r.listeners AS room_listeners, \
                     r.roomid AS roomid, \
                     r.downvotes, \
                     r.upvotes, \
                     r.current_dj AS current_dj_id, \
                     s.id AS song_id, \
                     s.nb_play AS room_nb_play, \
                     s.length AS song_length, \
                     s.song AS song_name, \
                     s.album AS song_album, \
                     s.artist AS song_artist, \
                     s.coverart AS song_coverart, \
                     u.name AS current_dj \
                   FROM rooms AS r \
                   LEFT JOIN songs AS s \
                     ON s.id = r.current_song \
                   LEFT JOIN users AS u \
                     ON u.id = r.current_dj \
                   WHERE %s='%s' \
                   LIMIT 1" % (where, str(shortcut)))

   # Raise 404 if no entry has been found.
   count = cursor.rowcount
   if count != 1:
      raise Http404

   room = dict_cursor(cursor)[0]
   room['song_length'] = format_length(room['song_length'])

   # itunes infos...
   data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (room['song_artist'], room['song_name']), 'entity':'song', 'limit':'1'})).read())
   if data['results']:
      room['previewUrl'] = data['results'][0].get('previewUrl')
      room['collectionViewUrl'] = data['results'][0].get('collectionViewUrl')

   return render_to_response('ajax_room_infos.html', {'room':room}, context_instance=RequestContext(req))


#def ajax_room_day_bests(req, limit):
#   cursor.execute("SELECT s.coverart, \
#                     s.id AS song_id, \
#                     s.song, \
#                     s.artist, \
#                     sl.upvotes, sl.downvotes, \
#                     sl.starttime, \
#                     sl.current_dj AS current_dj_id, \
#                     u.name AS current_dj \
#                   FROM songlog AS sl \
#                   LEFT JOIN songs AS s \
#                     ON s.id = sl.songid \
#                   LEFT JOIN users AS u \
#                     ON u.id = sl.current_dj \
#                   WHERE roomid=%s \
#                   ORDER BY starttime DESC \
#                   LIMIT %s, 20", [int(room['room_id']), limit])
#   songs = dict_cursor(cursor)
#   return songs


def ajax_room_day_appreciated(req):
   pass


def room(req, shortcut):
   if re.match('^\w{24}$', shortcut):
      where = 'r.roomid'
   else:
      where = 'r.shortcut'

   cursor = connection.cursor()

   cursor.execute("SELECT \
                     r.id AS room_id, \
                     r.name AS room_name, \
                     r.description AS room_description, \
                     r.shortcut AS room_shortcut, \
                     r.listeners AS room_listeners, \
                     r.roomid AS roomid, \
                     r.downvotes, \
                     r.upvotes, \
                     r.current_dj AS current_dj_id, \
                     r.current_dj_name AS current_dj, \
                     r.current_song AS CALISS, \
                     s.id AS song_id, \
                     s.nb_play AS room_nb_play, \
                     s.length AS song_length, \
                     s.song AS song_name, \
                     s.album AS song_album, \
                     s.artist AS song_artist, \
                     s.coverart AS song_coverart \
                   FROM rooms AS r \
                   LEFT JOIN songs AS s \
                     ON s.id = r.current_song \
                   WHERE %s='%s' \
                   LIMIT 1" % (where, str(shortcut)))

   # Raise 404 if no entry has been found.
   count = cursor.rowcount
   if count != 1:
      raise Http404

   room = dict_cursor(cursor)[0]
   room['song_length'] = format_length(room['song_length'])

   # itunes infos...
   try:
      data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (room['song_artist'], room['song_name']), 'entity':'song', 'limit':'1'})).read())
      if data['results']:
         room['previewUrl'] = data['results'][0].get('previewUrl')
         room['collectionViewUrl'] = data['results'][0].get('collectionViewUrl')
   except:
      pass

   if req.is_ajax():
      last = int(req.GET.get('last', 0))
      limit = last+1
   else:
      limit = 0

   cursor.execute("SELECT \
                     sl.song_coverart AS coverart, \
                     sl.song_id AS song_id, \
                     sl.song_name AS song, \
                     sl.song_artist AS artist, \
                     sl.upvotes, sl.downvotes, \
                     sl.dj AS current_dj_id, \
                     sl.dj_name AS current_dj \
                   FROM song_log AS sl \
                   WHERE sl.room_id=%s \
                   ORDER BY sl.created DESC \
                   LIMIT 20 OFFSET %s", [room['room_id'], limit])
   songs_log = dict_cursor(cursor)

   content = {'room':room, 'songs_log':songs_log}


   if not req.is_ajax():
      cursor.execute("SELECT sl.listeners, sl.created \
                      FROM song_log AS sl \
                      WHERE sl.room_id=%s \
                        AND sl.created::date = CURRENT_DATE \
                      ORDER BY sl.created", [room['room_id']])
      room_stats = dict_cursor(cursor)
      print room_stats;

      content.update({'room_stats': room_stats})


   if req.is_ajax():
      content.update({'last':last})
      return render_to_response('ajax_room.html', content, context_instance=RequestContext(req))
   else:
      content.update({'onglet':'rooms'})
      return render_to_response('room.html', content, context_instance=RequestContext(req))


def rooms(req):
   cursor = connection.cursor()


   if not cache.get('rooms_ups'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) AS upvotes, \
                        r.id AS room_id, \
                        r.roomid AS roomid, \
                        r.name AS room_name, \
                        r.listeners AS room_listeners, \
                        r.shortcut AS room_shortcut, \
                        r.upvotes AS song_upvotes, \
                        r.downvotes AS song_downvotes \
                      FROM rooms AS r \
                      LEFT JOIN song_log AS sl \
                        ON sl.room_id = r.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY r.id, r.roomid, r.name, r.listeners, r.shortcut, \
                        r.upvotes, r.downvotes \
                      ORDER BY upvotes DESC \
                      LIMIT 10")
      ups = dict_cursor(cursor)
      cache.set('rooms_ups', ups, 60*15)
   else:
      ups = cache.get('rooms_ups')


   if not cache.get('rooms_downs'):
      cursor.execute("SELECT \
                        SUM(sl.downvotes) AS downvotes, \
                        r.id AS room_id, \
                        r.roomid AS roomid, \
                        r.name AS room_name, \
                        r.listeners AS room_listeners, \
                        r.shortcut AS room_shortcut, \
                        r.upvotes AS song_upvotes, \
                        r.downvotes AS song_downvotes \
                      FROM rooms AS r \
                      LEFT JOIN song_log AS sl \
                        ON sl.room_id = r.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY r.id, r.roomid, r.name, r.listeners, r.shortcut, \
                        r.upvotes, r.downvotes \
                      ORDER BY downvotes DESC \
                      LIMIT 10")
      downs = dict_cursor(cursor)
      cache.set('rooms_downs', downs, 60*15)
   else:
      downs = cache.get('rooms_downs')


   if not cache.get('rooms_combined'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) - SUM(sl.downvotes) AS votes, \
                        r.id AS room_id, \
                        r.roomid AS roomid, \
                        r.name AS room_name, \
                        r.listeners AS room_listeners, \
                        r.shortcut AS room_shortcut, \
                        r.upvotes AS song_upvotes, \
                        r.downvotes AS song_downvotes \
                      FROM rooms AS r \
                      LEFT JOIN song_log AS sl \
                        ON sl.room_id = r.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY r.id, r.roomid, r.name, r.listeners, r.shortcut, \
                        r.upvotes, r.downvotes \
                      ORDER BY votes DESC \
                      LIMIT 10")
      combined = dict_cursor(cursor)
      cache.set('rooms_combined', combined, 60*15)
   else:
      combined = cache.get('rooms_combined')


   if not cache.get('rooms_active'):
      cursor.execute("SELECT \
                        AVG(sl.upvotes + sl.downvotes) AS moyenne, \
                        r.id AS room_id, \
                        r.roomid AS roomid, \
                        r.name AS room_name, \
                        r.listeners AS room_listeners, \
                        r.shortcut AS room_shortcut \
                      FROM rooms AS r \
                      LEFT JOIN song_log AS sl \
                        ON sl.room_id = r.id \
                      WHERE \
                        sl.dj IS NOT NULL AND \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY r.id, r.roomid, r.name, r.listeners, r.shortcut, \
                        r.upvotes, r.downvotes \
                      ORDER BY moyenne DESC \
                      LIMIT 10")
      active = dict_cursor(cursor)
      cache.set('rooms_active', active, 60*15)
   else:
      active = cache.get('rooms_active')

   return render_to_response('rooms.html', {'onglet':'rooms', 'ups':ups, 'downs':downs, 'combined':combined, 'active':active}, context_instance=RequestContext(req))


def user_fbid(req, fbid):
   cursor = connection.cursor()

   # Get infos about the user.
   cursor.execute("SELECT id \
                   FROM users AS u \
                   WHERE u.fbid=%s \
                   LIMIT 1", [int(fbid)])
   user_id = dict_cursor(cursor)[0]['id']
   return user(req, user_id)


def user_uid(req, uid):
   cursor = connection.cursor()

   # Get infos about the user.
   cursor.execute("SELECT id \
                   FROM users AS u \
                   WHERE u.userid=%s \
                   LIMIT 1", [uid])
   user_id = dict_cursor(cursor)[0]['id']
   return user(req, user_id)


def user(req, user_id):
   cursor = connection.cursor()

   # Get infos about the user.
   cursor.execute("SELECT * \
                   FROM users AS u \
                   WHERE u.id=%s \
                   LIMIT 1" % (int(user_id)))
   user = dict_cursor(cursor)[0]

   # Get how many up and down he got as a DJ.
   cursor.execute("SELECT SUM(sl.upvotes) AS upvotes, \
                     SUM(sl.downvotes) AS downvotes \
                   FROM song_log AS sl \
                   WHERE sl.dj=%s \
                   LIMIT 1" % (int(user_id)))
   votes = dict_cursor(cursor)[0]
   user['upvotes'] = votes['upvotes']
   user['downvotes'] = votes['downvotes']

   # Songs that the user has played.
   cursor.execute("SELECT \
                     sl.created, \
                     sl.upvotes, \
                     sl.downvotes, \
                     r.name AS room_name, \
                     r.roomid AS roomid, \
                     r.shortcut AS room_shortcut, \
                     sl.song_id AS song_id, \
                     sl.song_name AS song_name, \
                     sl.song_artist AS song_artist, \
                     sl.song_coverart AS song_coverart, \
                     sl.song_album AS song_album \
                   FROM song_log AS sl \
                   LEFT JOIN rooms AS r \
                     ON r.id = sl.room_id \
                   WHERE sl.dj=%s \
                   ORDER BY sl.created DESC \
                   LIMIT 30" % (int(user_id)))
   songs_log = dict_cursor(cursor)
   
      # Songs that the user like.
   cursor.execute("SELECT \
                     sl.song_id, \
                     sl.nb_awesomes AS nb, \
                     s.id AS song_id, \
                     s.song AS song_name, \
                     s.artist AS song_artist, \
                     s.genre AS song_genre, \
                     s.coverart AS song_coverart, \
                     s.album AS song_album \
                   FROM users_songs_liked AS sl \
                   LEFT JOIN songs AS s \
                     ON s.id = sl.song_id \
                   WHERE sl.user_id='%s' \
                     AND sl.nb_awesomes > 0 \
                   ORDER BY nb_awesomes DESC, sl.modified DESC \
                   LIMIT 30" % int(user_id))
   songs_like = dict_cursor(cursor)

   # Songs that the user dislike.
   cursor.execute("SELECT \
                     sl.song_id, \
                     sl.nb_lames AS nb, \
                     s.id AS song_id, \
                     s.song AS song_name, \
                     s.artist AS song_artist, \
                     s.genre AS song_genre, \
                     s.coverart AS song_coverart, \
                     s.album AS song_album \
                   FROM users_songs_liked AS sl \
                   LEFT JOIN songs AS s \
                     ON s.id = sl.song_id \
                   WHERE sl.user_id='%s' \
                     AND sl.nb_lames > 0 \
                   ORDER BY nb_lames DESC, sl.modified DESC \
                   LIMIT 30" % int(user_id))
   songs_dislike = dict_cursor(cursor)

   cursor.execute("SELECT \
                     COUNT(*) AS rank \
                   FROM users AS u \
                   WHERE u.id NOT IN (11717, 139, 13248, 532, 580) AND u.points > %s", [user['points']])
   rank_points = dict_cursor(cursor)[0]['rank']+1

   cursor.execute("SELECT \
                     COUNT(*) AS rank \
                   FROM users AS u \
                   WHERE u.id NOT IN (6902) AND u.fans > %s", [user['fans']])
   rank_fans = dict_cursor(cursor)[0]['rank']+1


   return render_to_response('user.html', { 'onglet':'users', 'tuser':user, 'songs_log':songs_log, 'songs_like':songs_like, 'songs_dislike':songs_dislike, 'rank_points':rank_points, 'rank_fans':rank_fans }, context_instance=RequestContext(req))


def ajax_uid_brag(req, uid):
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     id, \
                     name, \
                     laptop AS platform, \
                     userid, \
                     acl, \
                     fans, \
                     points, \
                     avatarid \
                   FROM users \
                   WHERE id = %s \
                   LIMIT 1", [uid])
   count = cursor.rowcount
   if count == 1:
      user = dict_cursor(cursor)[0]

      cursor.execute("SELECT \
                        COUNT(*) AS rank \
                      FROM users AS u \
                      WHERE u.id NOT IN (11717, 139, 13248, 532, 580) AND u.points > %s", [user['points']])
      rank_points = dict_cursor(cursor)[0]['rank']+1

      cursor.execute("SELECT \
                        COUNT(*) AS rank \
                      FROM users AS u \
                      WHERE u.id NOT IN (6902) AND u.fans > %s", [user['fans']])
      rank_fans = dict_cursor(cursor)[0]['rank']+1

      user['rank_points'] = rank_points
      user['rank_fans'] = rank_fans
   else:
      return render_to_response('ajax_brag.html', {'find':False}, context_instance=RequestContext(req))

   return render_to_response('ajax_brag.html', {'find':True, 'tuser':user}, context_instance=RequestContext(req))


def ajax_find_account(req, username):
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     id, \
                     name, \
                     laptop AS platform, \
                     userid, \
                     acl, \
                     fans, \
                     points, \
                     avatarid \
                   FROM users \
                   WHERE LOWER(name) LIKE %s \
                   LIMIT 30", ['%'+username.lower()+'%'])
   users = dict_cursor(cursor)

   return render_to_response('ajax_find_account.html', {'find':True, 'users':users}, context_instance=RequestContext(req))


def ajax_brag(req, username):
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     id, \
                     name, \
                     laptop AS platform, \
                     userid, \
                     acl, \
                     fans, \
                     points, \
                     avatarid \
                   FROM users \
                   WHERE name LIKE %s \
                   LIMIT 1", ['%'+username+'%'])
   count = cursor.rowcount
   if count == 1:
      user = dict_cursor(cursor)[0]

      cursor.execute("SELECT \
                        COUNT(*) AS rank \
                      FROM users AS u \
                      WHERE u.id NOT IN (11717, 139, 13248, 532, 580) AND u.points > %s", [user['points']])
      rank_points = dict_cursor(cursor)[0]['rank']+1

      cursor.execute("SELECT \
                        COUNT(*) AS rank \
                      FROM users AS u \
                      WHERE u.id NOT IN (6902) AND u.fans > %s", [user['fans']])
      rank_fans = dict_cursor(cursor)[0]['rank']+1

      user['rank_points'] = rank_points
      user['rank_fans'] = rank_fans
   else:
      return render_to_response('ajax_brag.html', {'find':False}, context_instance=RequestContext(req))

   return render_to_response('ajax_brag.html', {'find':True, 'tuser':user}, context_instance=RequestContext(req))



def chat(req, chatlog_id):
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     cl.id, \
                     cl.room_id AS log_roomid, \
                     cl.created, \
                     cl.user_id, \
                     u.id AS user_id, \
                     u.avatarid AS user_avatar, \
                     u.name AS user_name, \
                     u.laptop AS user_laptop, \
                     u.points AS user_points, \
                     u.fans AS user_fans, \
                     r.roomid AS roomid, \
                     r.shortcut AS room_shortcut, \
                     r.name AS room_name \
                   FROM chat_log AS cl \
                   LEFT JOIN users AS u \
                     ON u.id = cl.user_id \
                   LEFT JOIN rooms AS r \
                     ON r.id = cl.room_id \
                   WHERE cl.id=%s \
                   LIMIT 1", [chatlog_id])
   chatlog = dict_cursor(cursor)[0]

   cursor.execute("SELECT \
                     cl.id, \
                     cl.name, \
                     cl.created, \
                     cl.room_id, \
                     cl.user_id, \
                     cl.text \
                   FROM chat_log AS cl \
                   WHERE cl.room_id=%s \
                   AND cl.created > %s - INTERVAL '5' MINUTE \
                   AND cl.created < %s + INTERVAL '5' MINUTE \
                   ", [chatlog['log_roomid'], chatlog['created'], chatlog['created']])
   history = dict_cursor(cursor)

   return render_to_response('chat.html', {'chatlog':chatlog, 'history':history}, context_instance=RequestContext(req))


def thanks(req):
   return render_to_response('thanks.html', {}, context_instance=RequestContext(req))


def comments_and_suggestions(req):
   if req.method == 'POST': # If the form has been submitted...
      form = ContactForm(req.POST) # A form bound to the POST data
      if form.is_valid(): # All validation rules pass
         # Process the data in form.cleaned_data
         # ...
         message = str(req.POST['message']+' --> '+req.POST['sender'])
         send_mail('FEEDBACK FROM TTDASHBOARD', message, str(req.POST['sender']), ['alain.gilbert.15@gmail.com'], fail_silently=False)
         return HttpResponseRedirect('/thanks/') # Redirect after POST
   else:
      form = ContactForm() # An unbound form

   ctx = {}
   ctx.update(csrf(req))
   ctx.update({'form':form})
   return render_to_response('comments.html', ctx, context_instance=RequestContext(req))


def users(req):
   cursor = connection.cursor()

   if not cache.get('users_ups'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) AS upvotes, \
                        u.name, u.id, u.avatarid \
                      FROM users AS u \
                      LEFT JOIN song_log AS sl \
                        ON sl.dj = u.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.dj, u.name, u.id, u.avatarid \
                      ORDER BY upvotes DESC \
                      LIMIT 10")
      ups = dict_cursor(cursor)
      cache.set('users_ups', ups, 60*15)
   else:
      ups = cache.get('users_ups')


   if not cache.get('users_downs'):
      cursor.execute("SELECT \
                        SUM(sl.downvotes) AS downvotes, \
                        u.name, u.id, u.avatarid \
                      FROM users AS u \
                      LEFT JOIN song_log AS sl \
                        ON sl.dj = u.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.dj, u.name, u.id, u.avatarid \
                      ORDER BY downvotes DESC \
                      LIMIT 10")
      downs = dict_cursor(cursor)
      cache.set('users_downs', downs, 60*15)
   else:
      downs = cache.get('users_downs')


   if not cache.get('users_combined'):
      cursor.execute("SELECT \
                        SUM(sl.upvotes) - SUM(sl.downvotes) AS votes, \
                        u.name, u.id, u.avatarid \
                      FROM users AS u \
                      LEFT JOIN song_log AS sl \
                        ON sl.dj = u.id \
                      WHERE \
                        sl.created > CURRENT_DATE - INTERVAL '1' DAY \
                      GROUP BY sl.dj, u.name, u.id, u.avatarid \
                      ORDER BY votes DESC \
                      LIMIT 10")
      combined = dict_cursor(cursor)
      cache.set('users_combined', combined, 60*15)
   else:
      combined = cache.get('users_combined')

   return render_to_response('users.html', {'onglet':'users', 'ups':ups, 'downs':downs, 'combined':combined}, context_instance=RequestContext(req))


def users_appreciated(req):
   cursor = connection.cursor()
   if not cache.get('users_appreciated'):
      cursor.execute("SELECT * FROM users \
                      WHERE id NOT IN (11717, 139, 13248, 532, 580) \
                      ORDER BY points DESC LIMIT 100")
      appreciated = dict_cursor(cursor)
      cache.set('users_appreciated', appreciated, 60*15)
   else:
      appreciated = cache.get('users_appreciated')
   return render_to_response('users_appreciated.html', {'onglet':'users', 'appreciated':appreciated}, context_instance=RequestContext(req))


def users_popular(req):
   if not cache.get('users_popular'):
      cursor = connection.cursor()
      cursor.execute("SELECT * FROM users \
                      WHERE id NOT IN (6902) \
                      ORDER BY fans DESC LIMIT 100")
      popular = dict_cursor(cursor)
      cache.set('users_popular', popular, 60*15)
   else:
      popular = cache.get('users_popular')
   return render_to_response('users_popular.html', {'onglet':'users', 'popular':popular}, context_instance=RequestContext(req))


def hackaround(req):
   return render_to_response('hackaround.html', {})


def bookmarklet(req):
   return render_to_response('bookmarklet.html', {}, context_instance=RequestContext(req))


def terms(req):
   return render_to_response('terms.html', {}, context_instance=RequestContext(req))


def sidespeech(req):
   return render_to_response('sidespeech.html', {}, context_instance=RequestContext(req))


def itunes(req, artist, song_name):
   data = json.loads(urllib2.urlopen('http://itunes.apple.com/search?' + urllib.urlencode({'term':'%s %s' % (artist, song_name), 'entity':'song', 'limit':'25'})).read())
   return render_to_response('itunes.html', {'data':data}, context_instance=RequestContext(req))


def search(req):
   cursor = connection.cursor()

   search = req.GET.get('search', None)
   what = req.GET.get('what', None)

   if search == None or what == None:
      return render_to_response('search.html', {'results':[], 'what':what, 'search':search}, context_instance=RequestContext(req))

   db_search = "%%%s%%" % search.lower()

   if what == 'user':
      db_select = "*"
      db_from = "users"
      db_where = ['name']
   elif what == 'song':
      db_select = "*"
      db_from = "songs"
      db_where = ['album', 'artist', 'song', 'genre']
   elif what == 'chat':
      db_select = "cl.id, cl.user_id, cl.room_id, cl.name, cl.text, cl.created, r.id AS room_id, r.name AS room_name, r.shortcut AS room_shortcut"
      db_from = "chat_log AS cl LEFT JOIN rooms AS r ON r.id = cl.room_id"
      db_where = ['text']
   elif what == 'room':
      db_select = "*"
      db_from = "rooms"
      db_where = ['name', 'description']
   else:
      return render_to_response('search.html', {'results':[], 'what':what, 'search':search}, context_instance=RequestContext(req))

   # Generate sql where statement
   if what == 'chat':
      params = []
      params.append(db_search)
      db_where_gen = "text_tsv @@ to_tsquery(%s)"
   else:
      params = []
      db_where_gen = ''
      for w in db_where:
         params.append(db_search)
         db_where_gen += "LOWER(%s) LIKE %%s OR " % w
      db_where_gen = db_where_gen[:-4]

   # Our full querie
   rq = "SELECT "+db_select+" FROM "+db_from+" WHERE "+db_where_gen
   if what == 'chat':
      rq += ' ORDER BY created DESC'
   elif what == 'room':
      rq += ' ORDER BY listeners DESC'

   if req.is_ajax():
      last = int(req.GET.get('last', 0))
      rq += ' LIMIT 30 OFFSET %s' % last
   else:
      rq += ' LIMIT 30 OFFSET 0'

   cursor.execute(rq, params)
   results = dict_cursor(cursor)

   for result in results:
      for field in db_where:
         result['%s_highlight' % field] = escape(result[field])
         result['%s_highlight' % field] = re.sub(r"(?i)(%s)" % re.escape(search.lower()), lambda m: '<span class="highlight">%s</span>' % m.group(1), result['%s_highlight' % field], re.IGNORECASE)

   content = {'results':results, 'what':what, 'search':search}

   if req.is_ajax():
      content.update({'last':last})
      return render_to_response('ajax_search.html', content, context_instance=RequestContext(req))
   else:
      return render_to_response('search.html', content, context_instance=RequestContext(req))


def get_battle_infos():
   cursor = connection.cursor()
   roomid = '4e2a48c114169c27bb3e63cd'
   content = {}

   cursor.execute("SELECT r.id AS room_id, r.name AS room_name, \
                     r.description AS room_description, \
                     r.shortcut AS room_shortcut, \
                     r.listeners AS room_listeners, \
                     r.roomid AS roomid, \
                     r.downvotes, \
                     r.upvotes, \
                     r.current_dj AS current_dj_id, \
                     s.id AS song_id, \
                     s.nb_play AS room_nb_play, \
                     s.length AS song_length, \
                     s.song AS song_name, \
                     s.album AS song_album, \
                     s.artist AS song_artist, \
                     s.coverart AS song_coverart, \
                     u.name AS current_dj \
                   FROM rooms AS r \
                   LEFT JOIN songs AS s \
                     ON s.id = r.current_song \
                   LEFT JOIN users AS u \
                     ON u.id = r.current_dj \
                   WHERE r.roomid=%s \
                   LIMIT 1", [roomid])
   room = dict_cursor(cursor)[0]
   room['song_length'] = format_length(room['song_length'])
   content.update({'room':room})

   cursor.execute("SELECT s.coverart, \
                     s.id AS song_id, \
                     s.song, \
                     s.artist, \
                     sl.upvotes, sl.downvotes, \
                     sl.starttime, \
                     sl.current_dj AS current_dj_id, \
                     u.name AS current_dj \
                   FROM songlog AS sl \
                   LEFT JOIN songs AS s \
                     ON s.id = sl.songid \
                   LEFT JOIN users AS u \
                     ON u.id = sl.current_dj \
                   WHERE roomid=%s \
                   ORDER BY starttime DESC \
                   LIMIT 0, 20", [int(room['room_id'])])
   songs_log = dict_cursor(cursor)
   content.update({'songs_log':songs_log})

   cursor.execute("SELECT \
                     u.name, \
                     u.id, \
                     u.laptop, \
                     u.fans, \
                     u.points, \
                     u.avatarid, \
                     SUM(sl.upvotes) AS dj_upvotes, \
                     SUM(sl.downvotes) AS dj_downvotes \
                   FROM users AS u \
                   LEFT JOIN songlog AS sl \
                     ON starttime BETWEEN '2011-07-29 05:20:00' AND '2011-07-29 08:00:00' AND sl.current_dj = u.id AND roomid = %s \
                   WHERE id IN (7, 5, 108434, 1011, 35232) \
                   GROUP BY u.id \
                   LIMIT 5 \
                  ", [room['room_id']])
   djs = dict_cursor(cursor)
   for dj in djs:
      dj['dj_upvotes'] = dj['dj_upvotes'] if dj['dj_upvotes'] else 0
      dj['dj_downvotes'] = dj['dj_downvotes'] if dj['dj_downvotes'] else 0
   content.update({'djs':djs})

   return content


def ajax_battle(req):
   if not req.is_ajax():
      raise Http404

   content = {}

   if not cache.get('battle'):
      battle_infos = get_battle_infos()
      cache.set('battle', battle_infos, 10)
   else:
      battle_infos = cache.get('battle')

   content.update(battle_infos)
   return render_to_response('ajax_battle.html', content, context_instance=RequestContext(req))


def battle(req):
   content = {}

   if not cache.get('battle'):
      battle_infos = get_battle_infos()
      cache.set('battle', battle_infos, 10)
   else:
      battle_infos = cache.get('battle')

   content.update(battle_infos)
   return render_to_response('battle.html', content, context_instance=RequestContext(req))
