DROP TABLE if EXISTS users;

CREATE TABLE users (
	user text,
	email text,
	password text
);

DROP TABLE if EXISTS blogables;

CREATE TABLE blogables (
	user text,
	title text,
	post text,
	date text
);