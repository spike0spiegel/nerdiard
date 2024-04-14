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


def create_live_game(player_1_id, player_2_id: int) -> str:
    """Функция создаёт активную игру чтобы к ней можно обращаться для взятия id.
    В таблице активных игр только 1 столбец,записи в котором будут стираться и удаляться.
     game_id это комбинация двух player_id и даты-времени начала партии"""
    from datetime import datetime
    game_id = f"{player_1_id}_{player_2_id}_{datetime.now().date()}_{datetime.now().time().strftime('%H:%M:%S')}"

    query = """ INSERT INTO live_games
                VALUES ({game_id})
                ON CONFLICT DO NOTHING""".format(game_id=game_id)
    cursor = conn.cursor()
    cursor.execute('SET search_path TO nerdiard')
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return game_id

def
