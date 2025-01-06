CREATE TABLE customers (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	phone INTEGER NULL
)

SELECT * FROM customers

INSERT INTO customers(name, email) VALUES ('roman', 'aboba@e.huy')

ALTER TABLE customers ADD password VARCHAR(255);

SELECT name, email, password
FROM customers
WHERE (name='sinny' AND password='dick');