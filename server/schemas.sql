CREATE TABLE users (
   id                bigserial NOT NULL,
   userid            character varying(40) UNIQUE NOT NULL,
   name              character varying(255) NOT NULL,
   created           timestamp with time zone NOT NULL,
   laptop            character varying(20) NOT NULL,
   acl               int DEFAULT 0 NOT NULL,
   fans              int DEFAULT 0 NOT NULL,
   points            int DEFAULT 0 NOT NULL,
   avatarid          int DEFAULT 0 NOT NULL,

   CONSTRAINT        users_pk PRIMARY KEY (id)
);


CREATE TABLE songs (
   id                bigserial NOT NULL,
   songid            character varying(40) UNIQUE NOT NULL,
   album             character varying(255),
   artist            character varying(255),
   song              character varying(255),
   coverart          character varying(255),
   length            int DEFAULT 0 NOT NULL,
   mnid              int,
   genre             character varying(255),
   filepath          character varying(255),
   bitrate           int,

   nb_play           int DEFAULT 0 NOT NULL,

   CONSTRAINT        songs_pk PRIMARY KEY (id)
);


CREATE TABLE rooms (
   id                      bigserial NOT NULL,
   roomid                  character varying(40) UNIQUE NOT NULL,
   name                    character varying(255) NOT NULL,
   created                 timestamp with time zone NOT NULL,
   shortcut                character varying(255),
   description             character varying(255),

   listeners               int DEFAULT 0 NOT NULL,
   upvotes                 int DEFAULT 0 NOT NULL,
   downvotes               int DEFAULT 0 NOT NULL,
   current_song            bigint NULL,
   current_song_name       character varying(255) NULL,
   song_starttime          timestamp with time zone NULL,
   current_dj              bigint NULL,
   current_dj_name         character varying(255),

   CONSTRAINT              rooms_pk PRIMARY KEY (id),

   CONSTRAINT              rooms_current_song_fk
                              FOREIGN KEY (current_song)
                              REFERENCES songs(id) ON DELETE CASCADE,

   CONSTRAINT              rooms_current_dj_fk
                              FOREIGN KEY (current_dj)
                              REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE chat_log (
   id                bigserial NOT NULL,
   user_id           bigint NOT NULL,
   room_id           bigint NOT NULL,
   name              character varying(255) NOT NULL,
   text              text NOT NULL,
   created           timestamp with time zone DEFAULT current_timestamp NOT NULL,

   CONSTRAINT        chat_log_pk PRIMARY KEY (id),

   CONSTRAINT        chat_log_user_id_fk
                        FOREIGN KEY (user_id)
                        REFERENCES users(id) ON DELETE CASCADE,

   CONSTRAINT        chat_log_room_id
                        FOREIGN KEY (room_id)
                        REFERENCES rooms(id) ON DELETE CASCADE
);


CREATE TABLE song_log (
   room_id           bigint NOT NULL,
   song_id           bigint NOT NULL,
   starttime         timestamp with time zone NOT NULL,
   upvotes           int DEFAULT 0 NOT NULL,
   downvotes         int DEFAULT 0 NOT NULL,
   dj                bigint NOT NULL,
   dj_name           character varying(255),
   dj_count          int DEFAULT 0 NOT NULL,
   listeners         int DEFAULT 0 NOT NULL,
   created           timestamp with time zone NOT NULL,

   CONSTRAINT        song_log_pk
                        PRIMARY KEY (room_id, song_id, starttime),

   CONSTRAINT        song_log_room_id_fk
                        FOREIGN KEY (room_id)
                        REFERENCES rooms(id) ON DELETE CASCADE,

   CONSTRAINT        song_log_song_id_fk
                        FOREIGN KEY (song_id)
                        REFERENCES songs(id) ON DELETE CASCADE,

   CONSTRAINT        song_log_dj_fk
                        FOREIGN KEY (dj)
                        REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE users_songs_liked (
   user_id           bigint NOT NULL,
   song_id           bigint NOT NULL,
   nb_aesomes        int DEFAULT 0 NOT NULL,
   nb_lames          int DEFAULT 0 NOT NULL,
   modified          timestamp with time zone DEFAULT current_timestamp NOT NULL,

   CONSTRAINT        users_songs_liked_pk PRIMARY KEY (user_id, song_id),

   CONSTRAINT        users_songs_liked_user_id_fk
                        FOREIGN KEY (user_id)
                        REFERENCES users(id),

   CONSTRAINT        users_songs_liked_song_id_fk
                        FOREIGN KEY (song_id)
                        REFERENCES songs(id)
);
