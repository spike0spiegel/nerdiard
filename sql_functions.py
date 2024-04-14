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
