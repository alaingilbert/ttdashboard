from ids import FALSE_IDS
import psycopg2
from settings import *
import sys
import random

def main():

   if len(sys.argv) < 2:
      print "Not enought params."
      return

   conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (PG_DBNAME, PG_USER, PG_HOST, PG_PASSW))
   conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
   pc = conn.cursor()


   roomid = sys.argv[1]
   if len(roomid) < 24:
      print "Roomid invalid."
      pc.close()
      conn.close()
      return

   pc.execute("SELECT * FROM bots WHERE roomid=%s", (roomid,))
   rows = pc.fetchall()
   if len(rows) > 0:
      print "Room already on the table."
      pc.close()
      conn.close()
      return

   find = False
   while not find:
      userid, auth = random.choice(FALSE_IDS)
      pc.execute("SELECT * FROM bots WHERE userid=%s", (userid,))
      rows = pc.fetchall()
      if len(rows) == 0: find = True


   pc.execute("INSERT INTO bots (userid, auth, roomid) VALUES (%s, %s, %s)", (userid, auth, roomid))
   print "room added"
   pc.close()
   conn.close()


if __name__ == '__main__':
   main()
