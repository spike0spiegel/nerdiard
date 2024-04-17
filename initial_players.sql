SELECT DISTINCT player_1_id FROM games
UNION 
SELECT DISTINCT player_2_id FROM games;

SELECT * FROM shots ;


INSERT INTO players (player_id, player_username, player_active_status)
VALUES ('1992480617', Null, False); 

WITH player_accuracy_cte AS ( 
                SELECT player_1_accuracy AS accuracy
                FROM games
                WHERE player_1_id = '1992480617'
                UNION ALL
                SELECT player_2_accuracy AS accuracy
                FROM games
                WHERE player_2_id ='1992480617')
                SELECT ROUND(AVG(accuracy), 2)
                FROM player_accuracy_cte
                
                
UPDATE players 
SET player_active_status = NOT player_active_status
WHERE player_id = '1992480617'        





UPDATE players
SET player_active_status = FALSE  
WHERE player_id = '422838996';
