CREATE TABLE customers (
	id SERIAL PRIMARY KEY,
	login VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(255) NULL,
	basket VARCHAR(255) NOT NULL
);

CREATE TABLE products (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	price VARCHAR(255) NOT NULL,
	description VARCHAR(255) NULL
);

SELECT * FROM login;

INSERT INTO customers(login, email, password, basket) VALUES ('roman', 'aboba@e.huy', '123', '');

ALTER TABLE customers ADD password VARCHAR(255);

SELECT login, email, password
FROM customers
WHERE (login='Romannn' AND password='123456');