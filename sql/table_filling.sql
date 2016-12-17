INSERT INTO shop (adress, "name", cellphone, email)
	VALUES ('Botanicheskaya 64/3', 'SuperLamp', '2347891', 'super-lamp.ru'),
	('Pargolovskaya 37', 'Vsyo dlya doma', '4982789', 'vdd.com'),
	('Pobedy 1', 'Svet v okne', '8109360', 'svetvokne.ru');

INSERT INTO "type" ("name")
	VALUES ('lamp'), ('lightbulb'), ('illuminator'), ('torchere'), ('outdoor illumination');

INSERT INTO diller (adress, company, cellphone)
	VALUES ('Dachnaya 19', 'SilverBird', '+79098761212');
INSERT INTO diller (adress, company, cellphone, email)
	VALUES ('Kosmonavtov 9', 'Ogonek', '7683352', 'ogonek33@mail.ru'),
	('Tihomirova 20', 'AndreenkoComp', '+79094568989', 'avandreenko@yandex.ru'),
	('Poetov 15', 'TriTroyki', '2234591', 'yanova@gmail.com');


INSERT INTO product (type_id, "name", articul, color, price, number_left, diller_id, shop_id)
	VALUES (1, 'Bright Flower', 'A365BB', 'dark blue', 1725.50, 32, 1, 1),
	(1, 'SunLight', 'GH78992LI', 'orange', 2500.0, 20, 2, 3),
	(5, 'IdeaLight', '244980', 'blue', 175.0, 2, 1, 2),
	(2, 'Minion', '234', 'white', 50.0, 190, 4, 1),
	(2, 'Energysaving', '125', 'yellow', 190.0, 170, 4, 2),
	(3, 'KidBra', 'KO9898P', 'colorful', 3100.0, 12, 3, 3),
	(4, 'Garsia', 'SL678M', 'broun', 5723.10, 2, 2, 2),
	(1, 'Linvel', 'YX2786T', 'bright red', 540.20, 1, 1, 3),
	(1, 'Maxisvet', 'H224H', 'black', 701.70, 10, 2, 1),
	(4, 'Ecola', '56337', 'purple', 300.0, 12, 1, 1),
	(5, 'Umbrella', 'QW9908', 'mandarin', 1299.20, 5, 2, 2),
	(5, 'Feron', 'I6789M', 'antique gold', 12000.0, 1, 3, 3),
	(3, 'Italmac', 'P9078PP', 'silver sky', 234.50, 1, 4, 3),
	(3, 'Bohemia', '98982', 'grey', 902.90, 4, 4, 1),
	(3, 'Ice', '44563', 'green grass', 7000.0, 3, 1, 1),
	(1, 'Montana', 'Y89777P', 'BW strips', 590.20, 80, 4, 3),
	(1, 'Olympia', 'UI6129', 'milky green', 544.70, 21, 4, 3),
	(1, 'Venecia', 'MZ9090', 'white', 387.10, 12, 2, 2),
	(1, 'Verona', 'LIL144', 'violet', 2017.90, 30, 4, 2),
	(4, 'Techno', 'UU4653', 'silver', 3489.50, 20, 1, 1);
	

INSERT INTO customer ("name", adress, cellphone)
	VALUES ('Barsukov S.A.', 'Nekrasova 36', '+79817869080'),
	('Frolov E.G.', 'Chicherina 5', '239884'),
	('Perepelov G.K.', 'Bohnyaka 11', '+78957893434'),
	('Zubenko E.O.', 'Lenina 5', '9801786');

INSERT INTO worker ("name", shop_id, cellphone)
	VALUES ('Mihalkov A.F.', 1, '6874567'),
	('Fillipov A.F.', 1, '98288371'),
	('Frolov P.I.', 2, '2348920');
INSERT INTO worker ("name", shop_id, cellphone, email)
	VALUES ('Piskunov V.A.', 3, '469964', 'foxsay@gmail.com');

INSERT INTO "order" ("date", worker_id, customer_id)
	VALUES ('2016-10-05', 1, 1);

INSERT INTO order_position (product_id, qty, order_id)
	VALUES (1, 4, 1);




