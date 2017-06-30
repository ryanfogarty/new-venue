drop table if exists venues;
create table venues ( 
  id integer primary key autoincrement,
  venue_name text not null,
  venue_address text,
  venue_password text,
  venue_picture blob not null     
);