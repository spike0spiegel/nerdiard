--Вставка первых 4 столбцов
INSERT INTO games (game_id, game_time, player_1_id, player_2_id)
WITH 	cte_1 AS 	(SELECT DISTINCT game_id, player_id
					FROM shots
					ORDER BY game_id),
		cte_2 AS (SELECT game_id, player_id, ROW_NUMBER() OVER(PARTITION BY game_id) AS player_number FROM cte_1)
SELECT s.game_id, MAX(shot_time) - MIN(shot_time) AS game_time, c.player_id AS player_1_id, cc.player_id AS player_2_id
FROM shots s JOIN cte_2 c ON s.game_id = c.game_id AND c.player_number = 1
			 JOIN cte_2 cc ON s.game_id = cc.game_id AND cc.player_number = 2
GROUP BY s.game_id, c.player_id, cc.player_id
ORDER BY game_id;


--Вставка общего количества ударов для каждой партии
WITH cte AS (SELECT game_id, COUNT(*) AS shots_quantity 
			FROM shots 
			GROUP BY game_id)
UPDATE games 
SET shots_quantity = cte.shots_quantity
FROM cte
WHERE games.game_id = cte.game_id;

--Вставка общего количества чужих для каждой партии
WITH cte AS (SELECT game_id, COUNT(*) AS direct_shots_quantity 
			FROM shots
			WHERE shot_type = 'Ч'
			GROUP BY game_id)
UPDATE games 
SET direct_shots_quantity = cte.direct_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id;

--Вставка общего количества своих для каждой партии
WITH cte AS (SELECT game_id, COUNT(*) AS scratch_shots_quantity 
			FROM shots
			WHERE shot_type = 'С'
			GROUP BY game_id)
UPDATE games 
SET scratch_shots_quantity = cte.scratch_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id;

--Вставка общего количества отыгрышей для каждой партии
WITH cte AS (SELECT game_id, COUNT(*) AS safety_shots_quantity 
			FROM shots
			WHERE shot_type = 'О'
			GROUP BY game_id)
UPDATE games
SET safety_shots_quantity = COALESCE(cte.safety_shots_quantity, 0)
FROM cte
WHERE games.game_id = cte.game_id;

--Вставка нулей в столбец отыгрышей в тех партиях, где вообще не было отыгрышей
UPDATE games
SET safety_shots_quantity = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'О');

--Вставка количества всех ударов по первому игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_shots_quantity
			FROM shots 
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_shots_quantity = cte.player_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка количества всех ударов по второму игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_shots_quantity
			FROM shots 
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_shots_quantity = cte.player_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка количества чужих по первому игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_direct_shots_quantity
			FROM shots 
			WHERE shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_direct_shots_quantity = cte.player_direct_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка количества чужих по второму игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_direct_shots_quantity
			FROM shots 
			WHERE shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_direct_shots_quantity = cte.player_direct_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка количества своих по первому игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_scratch_shots_quantity
			FROM shots 
			WHERE shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_scratch_shots_quantity = cte.player_scratch_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка количества своих по второму игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_scratch_shots_quantity
			FROM shots 
			WHERE shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_scratch_shots_quantity = cte.player_scratch_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка количества отыгрышей по первому игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_safety_shots_quantity
			FROM shots 
			WHERE shot_type = 'О'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_safety_shots_quantity = cte.player_safety_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка нулей в столбец отыгрышей в тех партиях, где вообще не было отыгрышей (для игрока 1)
UPDATE games
SET player_1_safety_shots_quantity = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'О' AND player_id = games.player_1_id);

--Вставка количества отыгрышей по второму игроку
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_safety_shots_quantity
			FROM shots 
			WHERE shot_type = 'О'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_safety_shots_quantity = cte.player_safety_shots_quantity
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка нулей в столбец отыгрышей в тех партиях, где вообще не было отыгрышей (для игрока 2)
UPDATE games
SET player_2_safety_shots_quantity = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'О' AND player_id = games.player_2_id);


--Вставка количества всех точных ударов первого игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_shots
			FROM shots 
			WHERE shot_score != '0'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_scored = cte.player_fruitful_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка точности первого игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_1_id = g.player_id;

--Вставка количества точных чужих первого игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_direct_shots
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_direct_scored = cte.player_fruitful_direct_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка количества точных своих первого игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_scratch_shots
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_scratch_scored = cte.player_fruitful_scratch_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_1_id = cte.player_id;

--Вставка нулей в столбец своих в тех партиях, где не было точных своих (для игрока 1)
UPDATE games
SET player_1_scratch_scored = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'С' AND shot_score != 0 AND player_id = games.player_1_id);

--Вставка количества всех точных ударов второго игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_shots
			FROM shots 
			WHERE shot_score != '0'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_scored = cte.player_fruitful_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка точности второго игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_2_id = g.player_id;

--Вставка количества точных чужих второго игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_direct_shots
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_direct_scored = cte.player_fruitful_direct_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка количества точных своих второго игрока
WITH cte AS (SELECT player_id, game_id, COUNT(*) AS player_fruitful_scratch_shots
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_scratch_scored = cte.player_fruitful_scratch_shots
FROM cte
WHERE games.game_id = cte.game_id AND games.player_2_id = cte.player_id;

--Вставка нулей в столбец своих в тех партиях, где не было точных своих (для игрока 2)
UPDATE games
SET player_2_scratch_scored = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'С' AND shot_score != 0 AND player_id = games.player_2_id);

--Вставка точности чужих первого игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'Ч'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			WHERE shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_direct_shots_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_1_id = g.player_id;

--Вставка точности своих первого игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'С'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			WHERE shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_1_scratch_shots_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_1_id = g.player_id;

--Вставка нулей в столбец точности своих в тех партиях, где не было точных своих (для игрока 1)
UPDATE games
SET player_1_scratch_shots_accuracy = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'С' AND shot_score != 0 AND player_id = games.player_1_id);

--Вставка точности чужих второго игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'Ч'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			WHERE shot_type = 'Ч'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_direct_shots_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_2_id = g.player_id;

--Вставка точности своих второго игрока
WITH cte_good AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_fruitful_shots_quantity
			FROM shots 
			WHERE shot_score != '0' AND shot_type = 'С'
			GROUP BY game_id, player_id),
	cte_all AS (SELECT player_id,
			game_id,
			COUNT(*) AS player_shots_quantity
			FROM shots 
			WHERE shot_type = 'С'
			GROUP BY game_id, player_id)
UPDATE games 
SET player_2_scratch_shots_accuracy = (g.player_fruitful_shots_quantity::DOUBLE PRECISION / a.player_shots_quantity::DOUBLE PRECISION) * 100
FROM cte_good g JOIN cte_all a ON g.player_id = a.player_id AND g.game_id = a.game_id
WHERE games.game_id = g.game_id AND games.player_2_id = g.player_id;

--Вставка нулей в столбец точности своих в тех партиях, где не было точных своих (для игрока 2)
UPDATE games
SET player_2_scratch_shots_accuracy = 0
WHERE game_id NOT IN (SELECT game_id FROM shots WHERE shot_type = 'С' AND shot_score != 0 AND player_id = games.player_2_id);

SELECT *  FROM games ORDER BY game_id;


