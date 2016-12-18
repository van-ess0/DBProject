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
id serial NOT NULL primary key,
adress varchar(1000) NOT NULL,
"name" varchar(1000) NOT NULL,
cellphone varchar(80) NOT NULL,
email varchar(80)
);

CREATE TABLE "type" (
id serial NOT NULL primary key,
"name" varchar(1000) NOT NULL
);

CREATE TABLE diller (
id serial NOT NULL primary key,
adress varchar(1000) NOT NULL,
company varchar(1000) NOT NULL,
cellphone varchar(80),
email varchar(80)
);

CREATE TABLE product (
id serial NOT NULL primary key,
type_id int NOT NULL references "type"(id),
"name" varchar(80) NOT NULL,
articul varchar(80) NOT NULL,
color varchar(80),
price real NOT NULL CHECK (price > 0),
number_left int NOT NULL,
diller_id int references diller(id),
shop_id int references shop(id)
);

CREATE TABLE customer (
id serial NOT NULL primary key,
"name" varchar(1000) NOT NULL,
adress varchar(1000) NOT NULL,
cellphone varchar(80) NOT NULL,
email varchar(80),
pwd_hash varchar(40),
login varchar(80) NOT NULL UNIQUE
);

CREATE TABLE worker (
id serial NOT NULL primary key,
"name" varchar(1000) NOT NULL,
shop_id int references shop(id),
cellphone varchar(80) NOT NULL,
email varchar(80)
);

CREATE TABLE "order" (
id serial NOT NULL primary key,
"date" date NOT NULL,
worker_id int references worker(id),
customer_id int references customer(id)
);

CREATE TABLE order_position (
id serial NOT NULL primary key,
product_id int references product(id),
qty int NOT NULL CHECK (qty > 0),
order_id int references "order"(id),
UNIQUE (product_id, order_id)
);
