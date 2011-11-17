import psycopg2
import MySQLdb
from settings import *

conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (PG_DBNAME, PG_USER, PG_HOST, PG_PASSW))
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
pc = conn.cursor()

my_conn = MySQLdb.connect(MY_HOST, MY_USER, MY_PASSW, MY_DBNAME)
mc = my_conn.cursor(MySQLdb.cursors.DictCursor)


## Migrate the users.
#print "Start Users"
#mc.execute("SELECT * FROM users")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id       = row['id']
#   userid   = row['userid']
#   fbid     = row['fbid']
#   name     = row['name']
#   laptop   = row['laptop']
#   acl      = row['acl']
#   fans     = row['fans']
#   points   = row['points']
#   avatarid = row['avatarid']
#
#   try:
#      pc.execute("INSERT INTO users (id, userid, fbid, name, laptop, acl, fans, points, avatarid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, userid, fbid, name, laptop, acl, fans, points, avatarid))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate Users"
#
#
## Migrate the songs.
#print "Start Songs"
#mc.execute("SELECT * FROM songs")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id                = row['id']
#   songid            = row['songid']
#   album             = row['album']
#   artist            = row['artist']
#   coverart          = row['coverart']
#   song              = row['song']
#   length            = row['length']
#   mnid              = row['mnid']
#   genre             = row['genre']
#   filepath          = row['filepath']
#   bitrate           = row['bitrate']
#   nb_play           = row['nb_play']
#   previewurl        = row['previewurl']
#   collectionviewurl = row['collectionviewurl']
#
#   try:
#      pc.execute("INSERT INTO songs (id, songid, song, album, artist, coverart, length, mnid, genre, filepath, bitrate, nb_play, previewurl, collectionviewurl) \
#                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, songid, song, album, artist, coverart, length, mnid, genre, filepath, bitrate, nb_play, previewurl, collectionviewurl))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate Songs"
#
#
## Migrate the rooms.
#print "Start Rooms"
#mc.execute("SELECT * FROM rooms")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id             = row['id']
#   roomid         = row['roomid']
#   name           = row['name']
#   description    = row['description']
#   shortcut       = row['shortcut']
#   created        = row['created']
#
#   try:
#      pc.execute("INSERT INTO rooms (id, roomid, name, description, shortcut, created) VALUES (%s, %s, %s, %s, %s, %s)", (id, roomid, name, description, shortcut, created))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate Rooms"


## Migrate the users_songs_liked.
#print "Start Users_songs_liked"
#
#idx = 0
#i = 0
#while True:
#   mc.execute("SELECT * FROM users_songs_liked LIMIT %s,%s", (idx, 100000))
#   rows = mc.fetchall()
#   if len(rows) == 0: break
#   for row in rows:
#      if i % 10000 == 0: print "%s" % i
#      i += 1
#
#      user_id     = row['user_id']
#      song_id     = row['song_id']
#      nb_awesomes = row['nb_awesomes']
#      nb_lames    = row['nb_lames']
#
#      try:
#         pc.execute("INSERT INTO users_songs_liked (user_id, song_id, nb_awesomes, nb_lames) \
#                     VALUES (%s, %s, %s, %s)", (user_id, song_id, nb_awesomes, nb_lames))
#      except psycopg2.IntegrityError, e:
#         pass
#      except Exception, e:
#         print e
#   idx += 100000
#print "Terminate Users_songs_liked"
#
#
## Migrate the users_songs_liked.
#print "Start Song_log"
#idx = 0
#i = 0
#while True:
#   mc.execute("SELECT * FROM songlog LIMIT %s,%s", (idx, 100000))
#   rows = mc.fetchall()
#   if len(rows) == 0: break
#   for row in rows:
#      if i % 10000 == 0: print "%s" % i
#      i += 1
#
#      room_id       = row['roomid']
#      song_id       = row['songid']
#      upvotes       = row['upvotes']
#      downvotes     = row['downvotes']
#      current_dj    = row['current_dj']
#
#      try:
#         pc.execute("INSERT INTO song_log (room_id, song_id, upvotes, downvotes, dj) \
#                     VALUES (%s, %s, %s, %s, %s)", (room_id, song_id, upvotes, downvotes, current_dj))
#      except psycopg2.IntegrityError, e:
#         pass
#      except Exception, e:
#         print e
#   idx += 100000
#print "Terminate Song_log"


## Migrate the auth_user
#print "Start Auth_user"
#mc.execute("SELECT * FROM auth_user")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id           = row['id']
#   username     = row['username']
#   first_name   = row['first_name']
#   last_name    = row['last_name']
#   email        = row['email']
#   password     = row['password']
#   is_staff     = True if row['is_staff']     else False
#   is_active    = True if row['is_active']    else False
#   is_superuser = True if row['is_superuser'] else False
#   last_login   = row['last_login']
#   date_joined  = row['date_joined']
#
#   try:
#      pc.execute("INSERT INTO auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) \
#                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate"


## Migrate the website_userprofile
#print "Start Website_userprofile"
#mc.execute("SELECT * FROM website_userprofile")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id             = row['id']
#   user_id        = row['user_id']
#   ttuid          = row['ttuid']
#   activation_key = row['activation_key']
#   auth_key       = row['auth_key']
#
#   try:
#      pc.execute("INSERT INTO website_userprofile (id, user_id, ttuid, activation_key, auth_key, bandwidth) \
#                  VALUES (%s, %s, %s, %s, %s, 0)", (id, user_id, ttuid, activation_key, auth_key))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate"


# Migrate the playlists
#print "Start Playlists"
#mc.execute("SELECT * FROM playlists")
#rows = mc.fetchall()
#
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   id      = row['id']
#   uid     = row['uid']
#   created = row['created']
#   name    = row['name']
#   comment = row['comment']
#
#   try:
#      pc.execute("INSERT INTO playlists (id, uid, created, name, comment) \
#                  VALUES (%s, %s, %s, %s, %s)", (id, uid, created, name, comment))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate Playlists"


## Migrate the playlistsa_songs
#print "Start Playlists_songs"
#mc.execute("SELECT * FROM playlists_songs")
#rows = mc.fetchall()
#i = 0
#for row in rows:
#   if i % 10000 == 0: print "%s" % i
#   i += 1
#
#   song_id     = row['song_id']
#   playlist_id = row['playlist_id']
#   created     = row['created']
#   comment     = row['comment']
#
#   try:
#      pc.execute("INSERT INTO playlists_songs (song_id, playlist_id, created, comment) \
#                  VALUES (%s, %s, %s, %s)", (song_id, playlist_id, created, comment))
#   except psycopg2.IntegrityError, e:
#      pass
#   except Exception, e:
#      print e
#print "Terminate Playlists_songs"

print "Start Playlists_songs"
idx = 0
i = 0
while True:
   mc.execute("SELECT * FROM users LIMIT %s,%s", (idx, 10000))
   rows = mc.fetchall()
   if len(rows) == 0: break
   for row in rows:
      if i % 100 == 0: print "%s" % i
      i += 1

      userid = row['id']
      mc.execute("SELECT COUNT(*) AS hugs FROM chatlog WHERE userid=%s AND text LIKE '%%hugs%%'", (userid,))
      hugs = mc.fetchone()['hugs']

      try:
         pc.execute("UPDATE users SET hugs=%s WHERE id=%s", (hugs, userid))
      except psycopg2.IntegrityError, e:
         pass
      except Exception, e:
         print e
   idx += 10000
print "Terminate Playlists_songs"



mc.close()
my_conn.close()

pc.close()
conn.close()
