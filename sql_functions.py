import psycopg2


conn = psycopg2.connect(
    dbname='nerdiard',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432')


def get_player_accuracy(player_id: int) -> str:
    """Функция берёт айди из телеграма и по нему находит в дб общую точность игрока,
    который в использовал в боте команду shooting"""
    query = """ WITH player_accuracy_cte AS ( 
                SELECT player_1_accuracy AS accuracy
                FROM games
                WHERE player_1_id = '{player_id}'
                UNION ALL
                SELECT player_2_accuracy AS accuracy
                FROM games
                WHERE player_2_id ='{player_id}')
                SELECT ROUND(AVG(accuracy), 2)
                FROM player_accuracy_cte""".format(player_id=player_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return str(*data[0]) + '%'


def check_existing_player(player_id: int) -> bool:
    """Функция, которая проверяет, есть ли игрок, отправляющий какую-либо команду боту,
    в списке сыгравших хотя бы одну партию."""
    query = """ SELECT * 
                FROM players 
                WHERE player_id = '{player_id}' """.format(player_id=player_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return False
    else:
        return True


def check_active_player(player_id: int) -> bool:
    """Функция, которая проверяет, есть ли у игрока в данный момент запущенная партия."""
    query = """ SELECT * 
                FROM players 
                WHERE   player_id = '{player_id}'
                        and player_activestatus = True """.format(player_id=player_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return False
    else:
        return True


def switch_active_player(player_id: int) -> None:
    """Функция, которая переключает статус активности у игрока."""
    query = """ UPDATE players 
                SET player_active_status = NOT player_active_status
                WHERE player_id = '{player_id}'""".format(player_id=player_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return


def create_live_game(player_1_id, player_2_id: int, player_1_name, player_2_name: str) -> None:
    """Функция создаёт активную игру чтобы к ней можно обращаться для взятия id.
    В таблице активных игр только 1 столбец,записи в котором будут стираться и удаляться.
     game_id это комбинация двух player_id и даты-времени начала партии"""
    from datetime import datetime
    game_id = f"{player_1_id}_{player_2_id}_{datetime.now().date()}_{datetime.now().time().strftime('%H:%M:%S')}"

    query = """ INSERT INTO live_games 
                (game_id, player_1_id, player_2_id, player_1_name, player_2_name, player_1_score, player_2_score, shooter)
                VALUES 
                ({game_id}, {player_1_id}, {player_2_id}, {player_1_name}, {player_2_name}, 0, 0, Null)
                ON CONFLICT DO NOTHING""".format(game_id=game_id, player_1_id=player_1_id, player_2_id=player_2_id,
                                                 player_1_name=player_1_name, player_2_name=player_2_name)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return

def get_live_game_id(player_id: int) -> str:
    """Функция берёт из таблицы live_games game_id по player_id. В каждый момент времени там не может быть больше одной
    строки, в которой есть уникальный player_id"""
    query = """ SELECT game_id
                FROM live_games
                WHERE game_id LIKE '%{player_id}%'""".format(player_id=player_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    game_id = cursor.fetchall()
    cursor.close()
    return str(*game_id[0])

def set_shooter(game_id, shooter: str) -> None:
    """Функция, которая назначает бьющего."""
    query = """ UPDATE live_games
                SET shooter = {shooter} 
                WHERE game_id = '{game_id}'""".format(game_id=game_id, shooter=shooter)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return

def register_shot(game_id, shot_type, shot_score: str, shooter_id: int) -> None:
    """Функция, которая записывает одну строку в таблицу shots"""
    from datetime import datetime
    dt = datetime.now().time().strftime('%H:%M:%S')
    query = """ INSERT INTO shots (game_id, shot_time, player_id, shot_type, shot_score)
                VALUES ({game_id}, {dt}, {shooter_id}, {shot_type}, {shot_score})""".format(game_id=game_id,
                 player_id=shooter_id, shot_time=dt, shot_type=shot_type, shot_score=shot_score)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return

