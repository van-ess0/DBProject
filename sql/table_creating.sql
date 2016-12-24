\c postgres;

DROP DATABASE project;

CREATE DATABASE project
    WITH
    OWNER = "Van-ess0"
    ENCODING = 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8';

\c project;

CREATE TABLE shop (
id serial NOT NULL PRIMARY KEY,
adress varchar(1000) NOT NULL,
"name" varchar(1000) NOT NULL,
cellphone varchar(80) NOT NULL,
email varchar(80)
);

CREATE TABLE "type" (
id serial NOT NULL PRIMARY KEY,
"name" varchar(1000) NOT NULL
);

CREATE TABLE diller (
id serial NOT NULL PRIMARY KEY,
adress varchar(1000) NOT NULL,
company varchar(1000) NOT NULL,
cellphone varchar(80),
email varchar(80)
);

CREATE TABLE product (
id serial NOT NULL PRIMARY KEY,
type_id int NOT NULL REFERENCES "type"(id),
"name" varchar(80) NOT NULL,
articul varchar(80) NOT NULL,
color varchar(80),
price real NOT NULL CHECK (price >= 0),
number_left int NOT NULL CHECK (price >= 0),
diller_id int REFERENCES diller(id),
shop_id int REFERENCES shop(id)
);

CREATE TABLE customer (
id serial NOT NULL PRIMARY KEY,
"name" varchar(1000) NOT NULL,
adress varchar(1000) NOT NULL,
cellphone varchar(80) NOT NULL,
email varchar(80),
pwd_hash varchar(40),
login varchar(80) UNIQUE NOT NULL
);

CREATE TABLE worker (
id serial NOT NULL PRIMARY KEY,
"name" varchar(1000) NOT NULL,
-- shop_id int REFERENCES shop(id),
cellphone varchar(80) NOT NULL,
email varchar(80)
);

CREATE TABLE "order" (
id serial NOT NULL PRIMARY KEY,
"date" date NOT NULL,
worker_id int REFERENCES worker(id),
customer_id int REFERENCES customer(id)
);

CREATE TABLE order_position (
id serial NOT NULL PRIMARY KEY,
product_id int REFERENCES product(id),
qty int NOT NULL CHECK (qty > 0),
order_id int REFERENCES "order"(id) ON DELETE CASCADE,
UNIQUE (product_id, order_id)
);

CREATE TABLE feedback (
id serial NOT NULL PRIMARY KEY,
body text,
order_id int REFERENCES "order"(id) ON DELETE CASCADE
);
