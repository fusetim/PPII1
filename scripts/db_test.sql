INSERT INTO public.alembic_version (version_num) VALUES
	('34846deb5671');

INSERT INTO public.users (user_uid,username,"password",bio,creation_date,deletion_date,session_uid,display_name,avatar_uid) VALUES
	('a616d271-bff3-4443-bf4c-24169a7f0345','fusetim','$argon2id$v=19$m=65536,t=3,p=4$UaC5nyTN9vmJfPlstlhy6g$ITcqpVK8a0aZ66lvi5ah4Zo2MfCRYsbJAKIF+zkgn88','Développeur chez CuliVert, je façonne l''avenir de la gastronomie durable. Créateur du site web novateur dédié à la recherche de recettes, je mets l''accent sur l''empreinte carbone de chaque plat. Mon engagement vise à sensibiliser les utilisateurs à l''impact environnemental de leurs choix culinaires, favorisant ainsi une alimentation délicieuse et durable. Passionné de technologie, je fusionne ces deux mondes pour inspirer des choix culinaires éclairés et respectueux de l''environnement.','2023-12-20 14:41:17.67829',NULL,'9691ada9-f79e-4ba7-8260-34fdcc30c475','Timothée',NULL),
	('6434e9ce-8e46-48a2-9f2f-35699160f526','culivert','','CuliVert est une initiative étudiante développée à Nancy dont le but est d’accompagner les consommateurs dans la transition écologique, en collaboration avec l''association Enactus. Le projet CuliVert est né d''une volonté de rendre la cuisine plus écologique. Nous souhaitons vous aider à cuisiner des plats délicieux et respectueux de l'' environnement.','2023-12-20 15:39:11.422452',NULL,'d5ac0944-d1b7-4eb7-9a1a-c59098a47ca2','CuliVert','7d580492-cca9-4c7a-9cd1-18c9e5a9260a');

INSERT INTO public.recipes (recipe_uid,name,short_description,description,"type",author,normalized_name,duration,illustration_uid) VALUES
	('74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','Pâte à la sauce bolognaise','Savourez la délicieuse simplicité de notre recette de pâtes bolognaises maison. Des pâtes al dente rencontrent une sauce généreuse, mijotée avec amour. Laissez-vous envoûter par l''arôme enivrant de tomates mûres, d''ail et d''oignons, mariés à une viande de bœuf savamment assaisonnée.','1. **Cuisson des pâtes :** Faites cuire les pâtes selon les instructions sur l''emballage. Égouttez et réservez.

2. **Préparation de la sauce :** Dans une grande poêle, chauffez l''huile d''olive à feu moyen. Ajoutez l''oignon et l''ail, faites-les sauter jusqu''à ce qu''ils soient dorés.

3. **Cuisson de la viande :** Ajoutez la viande de bœuf hachée à la poêle et faites-la cuire jusqu''à ce qu''elle soit bien dorée. Éliminez l''excès de graisse.

4. **Sauce tomate :** Incorporer les tomates concassées, le concentré de tomate, le vin rouge, l''origan et le basilic. Assaisonnez avec du sel et du poivre. Laissez mijoter à feu doux pendant environ 20 minutes pour que les saveurs se mélangent.

5. **Assemblage :** Mélangez les pâtes cuites dans la sauce bolognaise. Assurez-vous que les pâtes sont bien enrobées de sauce.

6. **Service :** Servez les pâtes à la bolognaise dans des assiettes, garnissez de parmesan râpé et ajoutez des herbes fraîches si vous le souhaitez.

Profitez de ce délicieux plat italien fait maison !','plat','6434e9ce-8e46-48a2-9f2f-35699160f526','pate a la sauce bolognaise',30,NULL),
	('de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','Pizza maison (regina)','short_description','
# Confection de la Pâte à pizza

## Étape 1

Dans un saladier, placez la farine, puis la levure boulanger, la pincée de sel et celle de poivre. Ajoutez également le paprika et le sel d''ail selon votre goût. Mélangez à sec pour homogénéiser les ingrédients.

## Étape 2

Versez ensuite la moitié du dosage d''eau, remuez avec votre doigt. Ajoutez l''huile d''olive et versez enfin le reste de l''eau, puis remuez. Lorsque la pâte est collante, utilisez votre main pour mélanger le tout, jusqu''à obtenir une pâte collante sans reste de farine.

## Étape 3 - Pétrissage

Ajoutez alors un peu de farine à la main, mélangez et pétrissez. Recommencez l''opération (farine plus pétrissage) jusqu''à obtenir une boule de pâte qui ne colle plus.

![Pétrissage accomplie](//i.imgur.com/1MoHsDZl.jpg)

## Étape 4

Mettez un peu de farine au fond de votre saladier et sur ses côtés, puis remettez la boule dedans et couvrez avec un torchon propre.

## Étape 5 - Repos

Laissez reposer la pâte environ 2 heures (ou moins, voire pas du tout si vous êtes pressés).
Vous pouvez également laisser chauffer la pâte à base température (60°C) pendant 40 minutes
pour accélérer cette étape.

# Préparation de la pizza

## Étape 6

Mettez votre four à préchauffer à 220°C.
Sur votre plan de travail, étalez un peu de farine afin que la boule ne colle pas.

## Étape 7

Saupoudrez votre boule d''un peu de farine et sortez-la du saladier. Vous pouvez la découper en plusieurs morceaux si nécessaire.
Avec un rouleau à pâtisserie, faites-en un (ou des) disques d''environ 35 cm de diamètre.

## Étape 8

Posez la pâte ainsi formée sur votre plaque, avec en dessous du papier sulfurisé ou à défaut de la farine, pour que la pâte ne reste pas collée sur la plaque à la cuisson.

## Étape 9

Étalez la sauce tomate sur la pâte, jusqu''à ne presque plus voir la pâte au travers (2 à 3 mm d''épaisseur de sauce).

## Étape 10 - Garnissage

Repartissez ensuite la garniture de votre pizza. 
Commencez par le jambon (ou la viande de votre choix), puis répartissez le fromage rapé sur l''ensemble de la pizza. Vous pouvez ensuite ajouter de la mozzarella, du fromage de chèvre et/ou des olives.

## Étape 11 - Cuisson

Enfournez à mi-hauteur pendant 20 min pour une pâte plus plutôt croustillante.

## Étape 12 - Service

Sortez la pizza quand le fromage est bien fondu et commence à faire des bulles et à dorer. Découpez et servez.
','plat','a616d271-bff3-4443-bf4c-24169a7f0345','pizza maison',170,NULL);

INSERT INTO public.quantity_types (quantity_type_uid,name,localized_key,mass_equivalent,unit) VALUES
	('d9ce4269-0147-48df-a167-2e77f88106f7','Kilogramme','kilogramme',1.0,'kg'),
	('7ecd4f75-34de-4b79-a643-98bf1abea4d2','Litre','litre',1.0,'L'),
	('e7eea8ad-7eb9-473a-905a-35db9fb2e874','Gramme','gramme',0.001,'g'),
	('568995df-f014-48ea-a3d7-61e79d23ff6f','Once','once',0.0284,'oz'),
	('c69e580d-c117-4ef3-8615-10853d49859f','Livre','livre',0.454,'lb'),
	('5ac376e4-103b-4603-9998-80f94b2a4ce2','Millilitre','millilitre',0.001,'mL'),
	('95653137-1979-4c3f-903e-ed470bdef0ef','Centilitre','centilitre',0.01,'cL'),
	('e4ffedc3-0b11-4939-90ab-bc673fde5fe9','Tasse','tasse',0.237,' tasse(s)'),
	('330741df-4e90-4644-af5b-e8f8276d02a2','Cuillerée à soupe','cuilleree a soupe',0.014,' cuillère(s) à soupe'),
	('24ab4f11-5a86-41b7-9eea-981df7b85b9c','Cuillerée à café','cuilleree a cafe',0.00466,' cuillère(s) à café');
INSERT INTO public.quantity_types (quantity_type_uid,name,localized_key,mass_equivalent,unit) VALUES
	('9145af30-d107-4606-afc0-95a172e64f01','Pincée','pincee',0.0005,' pincée(s)'),
	('e7e73ded-e5af-4006-9add-2c0aaed3bf7b','Pièce','piece',0.0,' pièce(s)');


INSERT INTO public.ingredient_links (link_uid,recipe_uid,ingredient_code,quantity,quantity_type_uid,reference_quantity,display_name) VALUES
	('b570cc47-3f55-43b7-a6ac-d193db4d4142','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','20260',40.0,'95653137-1979-4c3f-903e-ed470bdef0ef',NULL,'Coulis de tomate'),
	('360411fc-ef64-423e-8d9a-a7f873d4f2da','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','6260',500.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Viande de bœuf hachée'),
	('5e0b44e8-2771-4319-aa81-999c36536daf','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','9810',350.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Pâtes de votre choix'),
	('9e48df83-b665-44df-a249-57d42af5c975','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','17270',10.0,'5ac376e4-103b-4603-9998-80f94b2a4ce2',0.01,'Huile d''olive'),
	('ed5e57c9-831e-4d2a-b3d2-afbf3429e576','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','20034',1.0,'e7e73ded-e5af-4006-9add-2c0aaed3bf7b',0.05,'Oignon'),
	('7759a70a-8366-4062-9079-91982717c609','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','11000',2.0,'e7e73ded-e5af-4006-9add-2c0aaed3bf7b',0.01,'Gousses d''ail'),
	('b07533de-7b47-457d-bed3-636982ce4bfe','74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','5214',50.0,'5ac376e4-103b-4603-9998-80f94b2a4ce2',NULL,'Vin rouge'),
	('1ea7d466-0705-4b10-b6a9-d865e7c53a58','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','28900',500.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Jambon blanc'),
	('f3a124ba-e3e6-4da2-bd2f-e3002608f5da','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','12113',400.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Fromage rapé'),
	('5adb5f96-3d12-4df1-8ef2-256cf100db5a','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','9436',600.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Farine (blanche ou complète)');
INSERT INTO public.ingredient_links (link_uid,recipe_uid,ingredient_code,quantity,quantity_type_uid,reference_quantity,display_name) VALUES
	('b65dd127-5588-4609-8b1f-55487a28f008','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','20260',40.0,'95653137-1979-4c3f-903e-ed470bdef0ef',NULL,'Coulis de tomate'),
	('2c2d1c0e-d978-4f91-8792-97b769439ba3','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','11045',40.0,'e7eea8ad-7eb9-473a-905a-35db9fb2e874',NULL,'Levure boulanger'),
	('4e208a4c-49a2-42a2-9725-1e0dccf9ee48','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','18430',40.0,'95653137-1979-4c3f-903e-ed470bdef0ef',NULL,'Eau'),
	('74b23de1-ea55-428e-910b-bf9fd6ff90d0','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','13147',16.0,'e7e73ded-e5af-4006-9add-2c0aaed3bf7b',0.08,'Olives vertes'),
	('256d6965-129c-407d-8ebc-f842b3c549f5','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','11058',3.0,'9145af30-d107-4606-afc0-95a172e64f01',NULL,'Sel'),
	('0e72c4c9-6f6d-4e43-a37d-b2b84f360908','de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','11015',1.0,'9145af30-d107-4606-afc0-95a172e64f01',NULL,'Poivre');

INSERT INTO public.recipe_tags (recipe_tag_uid,name,normalized_name) VALUES
	('57241f5a-da6d-4344-8174-b6b9e3a2d862','Facile','facile'),
	('ccc02c11-b727-4277-87c8-2e657b07f571','Complexe','complexe'),
	('ed61bb85-8523-4ae4-8c08-4c3de7acb818','Difficile','difficile'),
	('ce072047-0559-41f1-a881-9b5626c9b84d','EcoScore Bon','ecoscore bon'),
	('c058f06e-5cd5-496b-83d6-4eee05d47739','EcoScore Moyen','ecoscore moyen'),
	('262fe9bf-b3b2-4a76-84c9-67c5f5a42041','EcoScore Mauvais','ecoscore mauvais'),
	('646b2132-a9af-4825-a067-27006c28e0fd','Bon Marché','bon marche'),
	('e55a4463-9357-4986-b7df-e544eb0d55a6','Couteux','couteux'),
	('f54ae6fd-3491-466c-8845-ca33f0f7dc91','Abordable','abordable');

INSERT INTO public.recipe_tag_links (recipe_uid,recipe_tag_uid) VALUES
	('74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','57241f5a-da6d-4344-8174-b6b9e3a2d862'),
	('74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','c058f06e-5cd5-496b-83d6-4eee05d47739'),
	('74ebb1a7-9aa6-45e3-886f-a575bf4f1dc9','646b2132-a9af-4825-a067-27006c28e0fd'),
	('de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','57241f5a-da6d-4344-8174-b6b9e3a2d862'),
	('de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','c058f06e-5cd5-496b-83d6-4eee05d47739'),
	('de60f7b4-84c3-44d3-ac2f-36108b6c6fb1','646b2132-a9af-4825-a067-27006c28e0fd');

