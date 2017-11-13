create table users
(
	id INTEGER PRIMARY KEY AUTOINCREMENT not null,
	name TEXT not null,
	email TEXT not null,
	hash TEXT not null,
	salt TEXT not null
)
;

create unique index users_id_uindex
	on users (id)
;

create unique index users_email_uindex
	on users (email)
;


create table reviews
(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
	title TEXT not null,
	rating INTEGER not null,
	review TEXT not null,
	created_by INTEGER not null
		constraint reviews_users_id_fk
			references users (id),
	date_created DATETIME not null,
	upvotes INTEGER not null,
	downvotes INTEGER not null
)
;

create unique index reviews_id_uindex
	on reviews (id)
;

