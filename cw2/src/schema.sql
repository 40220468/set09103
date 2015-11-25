DROP TABLE if EXISTS users;

CREATE TABLE users (
	user text,
	email text,
	password text
);

CREATE TABLE blogables (
	user text,
	title text,
	post text,
	date text
);