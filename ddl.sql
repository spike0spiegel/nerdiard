DROP TABLE shots;
DROP TABLE games;
DROP TABLE players;

CREATE TABLE shots (
	game_id VARCHAR(50),
	shot_time varchar(20),
	player_id VARCHAR(15),
	shot_type VARCHAR(1),
	shot_score INTEGER);
	

COPY shots FROM 'D:/Projects/nerdiard/data.csv' WITH (format CSV);

ALTER TABLE shots
ALTER COLUMN shot_time TYPE time USING shot_time::time without time zone;

CREATE TABLE games (
	game_id VARCHAR(50) PRIMARY KEY,
	game_time INTERVAL,
	player_1_id VARCHAR(15),
	player_2_id VARCHAR(15),
	shots_quantity INT,
	direct_shots_quantity INT,
	scratch_shots_quantity INT,
	safety_shots_quantity INT,
	player_1_shots_quantity INT,
	player_1_direct_shots_quantity INT,
	player_1_scratch_shots_quantity INT,
	player_1_safety_shots_quantity INT,
	player_2_shots_quantity INT,
	player_2_direct_shots_quantity INT,
	player_2_scratch_shots_quantity INT,
	player_2_safety_shots_quantity INT,
	player_1_scored INT,
	player_1_direct_scored INT,
	player_1_scratch_scored INT,
	player_2_scored INT,
	player_2_direct_scored INT,
	player_2_scratch_scored INT,
	player_1_accuracy NUMERIC(5, 2),
	player_1_direct_shots_accuracy NUMERIC(5, 2),
	player_1_scratch_shots_accuracy NUMERIC(5, 2),
	player_2_accuracy NUMERIC(5, 2),
	player_2_direct_shots_accuracy NUMERIC(5, 2),
	player_2_scratch_shots_accuracy NUMERIC(5, 2));



CREATE TABLE players (
	player_id VARCHAR(15) PRIMARY KEY,
	player_username VARCHAR(50),
	player_active_status BOOLEAN);

CREATE TABLE live_games (
	game_id VARCHAR(50) PRIMARY KEY,
	player_1_id VARCHAR(15),
	player_2_id VARCHAR(15),
	player_1_name VARCHAR(20),
	player_2_name VARCHAR(20),
	player_1_score INT,
	player_2_score INT,
	shooter_id VARCHAR(15),
	shooter_name VARCHAR(20));


	