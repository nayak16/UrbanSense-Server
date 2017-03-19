drop table if exists entries;
create table entries (
	  id integer primary key autoincrement,
	  data_point integer not null,
	  'comment' text not null
);
