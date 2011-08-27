from django.shortcuts import get_object_or_404, render_to_response
from website.models import *
from website.forms import *
from django.db import connection, transaction
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.utils.html import escape
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
import re, json

def dict_cursor(cursor):
   description = [x[0] for x in cursor.description]
   rows = []
   for row in cursor:
      rows.append(dict(zip(description, row)))
   return rows


def user_name(req, username):
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
                      WHERE u.id NOT IN (139, 13248, 532, 580) AND u.points > %s", [user['points']])
      rank_points = dict_cursor(cursor)[0]['rank']+1

      user['rank_points'] = rank_points
   else:
      return HttpResponse(json.dumps({'error':'This username does not exists.'}), mimetype='application/javascript')

   return HttpResponse(json.dumps(user), mimetype='application/javascript')


def user_id(req, user_id):
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
                   LIMIT 1", [user_id])
   count = cursor.rowcount
   if count == 1:
      user = dict_cursor(cursor)[0]
   else:
      return HttpResponse(json.dumps({'error':'This user id does not exists.'}), mimetype='application/javascript')

   return HttpResponse(json.dumps(user), mimetype='application/javascript')


def user_ttid(req, user_ttid):
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
                   WHERE userid = %s \
                   LIMIT 1", [user_ttid])
   count = cursor.rowcount
   if count == 1:
      user = dict_cursor(cursor)[0]
   else:
      return HttpResponse(json.dumps({'error':'This user id does not exists.'}), mimetype='application/javascript')

   return HttpResponse(json.dumps(user), mimetype='application/javascript')


def room_shortcut(req, shortcut):
   cursor = connection.cursor()

   cursor.execute("SELECT \
                     r.id, \
                     r.roomid, \
                     r.name, \
                     r.created, \
                     r.description, \
                     r.shortcut, \
                     r.moderator_id, \
                     r.current_dj, \
                     r.listeners, \
                     r.downvotes, \
                     r.upvotes, \
                     r.song_starttime, \
                     r.current_song, \
                     u.id AS dj_id, \
                     u.name AS dj_name, \
                     u.laptop AS dj_platform, \
                     u.userid AS dj_userid, \
                     u.acl AS dj_acl, \
                     u.fans AS dj_fans, \
                     u.points AS dj_points, \
                     u.avatarid AS dj_avatarid, \
                     s.id AS song_id, \
                     s.songid AS song_ttid, \
                     s.album AS song_album, \
                     s.artist AS song_artist, \
                     s.coverart AS song_coverart, \
                     s.song AS song_name, \
                     s.length AS song_length, \
                     s.mnid AS song_mnid, \
                     s.genre AS song_genre, \
                     s.nb_play AS song_nb_play \
                   FROM rooms AS r \
                   LEFT JOIN users AS u \
                   ON u.id = r.current_dj \
                   LEFT JOIN songs AS s \
                   ON s.id = r.current_song \
                   WHERE r.shortcut = %s \
                   LIMIT 1", [shortcut])
   count = cursor.rowcount
   if count == 1:
      r = dict_cursor(cursor)[0]
      room = {'id':r['id'],
              'ttid':r['roomid'],
              'name':r['name'],
              'description':r['description'],
              'shortcut':r['shortcut'],
              'moderator_ttid':r['moderator_id'],
              'listeners':r['listeners'],
              'created':r['created'],
              'current_song':{'id':r['song_id'],
                              'name':r['song_name'],
                              'album':r['song_album'],
                              'artist':r['song_artist'],
                              'coverart':r['song_coverart'],
                              'length':r['song_length'],
                              'genre':r['song_genre'],
                              'nb_play':r['song_nb_play'],
                              'upvotes':r['upvotes'],
                              'downvotes':r['downvotes'],
                             },
              'current_dj':{'id':r['dj_id'],
                            'ttid':r['dj_userid'],
                            'name':r['dj_name'],
                            'platform':r['dj_platform'],
                            'fans':r['dj_fans'],
                            'points':r['dj_points'],
                            'avatarid':r['dj_avatarid']
                           }
             }
   else:
      return HttpResponse(json.dumps({'error':'This room shortcut does not exists.'}), mimetype='application/javascript')

   return HttpResponse(json.dumps(room, cls=DjangoJSONEncoder), mimetype='application/javascript')


def playlists(req):


   if not req.user.is_authenticated():
      obj = {'error': 'User not logged.'}
      return HttpResponse(json.dumps(obj, cls=DjangoJSONEncoder), mimetype='application/javascript')


   cursor = connection.cursor()

   user = req.user
   profile = user.get_profile()
   uid = profile.ttuid

   cursor.execute("SELECT \
                     id, \
                     name, \
                     comment, \
                     created \
                   FROM playlists \
                   WHERE uid = %s \
                  ", [user.id])
   count = cursor.rowcount
   playlists = dict_cursor(cursor)

   obj = {'playlists': []}
   for playlist in playlists:
      obj['playlists'].append({'id': playlist['id'], 'name': playlist['name'], 'comment': playlist['comment'], 'created': playlist['created']})

   return HttpResponse(json.dumps(obj, cls=DjangoJSONEncoder), mimetype='application/javascript')


def playlist(req, playlist_id):

   if not req.user.is_authenticated():
      obj = {'error': 'User not logged.'}
      return HttpResponse(json.dumps(obj, cls=DjangoJSONEncoder), mimetype='application/javascript')


   cursor = connection.cursor()
   
   user = req.user
   profile = user.get_profile()
   uid = profile.ttuid

   cursor.execute("SELECT id, comment, name, created \
                   FROM playlists \
                   WHERE id = %s AND uid = %s \
                   LIMIT 1 \
                  ", [playlist_id, req.user.id])


   if cursor.rowcount != 1:
      obj = {'error': 'Bad playlist id.'}
      return HttpResponse(json.dumps(obj, cls=DjangoJSONEncoder), mimetype='application/javascript')


   playlist = dict_cursor(cursor)[0]

   cursor.execute("SELECT \
                     s.songid, \
                     s.song AS name, \
                     s.album, \
                     s.artist, \
                     s.coverart \
                   FROM playlists_songs AS ps \
                   LEFT JOIN songs AS s \
                     ON s.id = ps.song_id \
                   WHERE playlist_id = %s \
                  ", [playlist_id])
   songs = dict_cursor(cursor)


   obj = {'playlist': {'id': playlist['id'],
                       'name': playlist['name'],
                       'comment': playlist['comment'],
                       'created': playlist['created']
                      },
          'songs': []
         }

   for song in songs:
      obj['songs'].append({'id': song['songid'], 'name': song['name'], 'album': song['album'], 'artist': song['artist'], 'coverart': song['coverart']})


   return HttpResponse(json.dumps(obj, cls=DjangoJSONEncoder), mimetype='application/javascript')


def home(req):
   return render_to_response('api/home.html', {})
