import telebot
from datetime import datetime
from telebot import types
import pandas as pd

bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
players_csv = 'D:/Projects/nerdiard/players.csv' #список всех пользователей бота
live_players = [] #список играющих в данных момент пользователей
data = 'D:/Projects/nerdiard/data.csv' #данные
active_games = {}


@bot.message_handler(commands=['start']) #обработка команды start и настройка кнопки menu
def handle_start(message):

    help_menu_command = types.BotCommand(command='help', description='Руководство.')
    newgame_menu_command = types.BotCommand(command='newgame', description='Начать новую партию.')
    register_player_menu_command = types.BotCommand(command='registerplayer', description='Зарегистрироваться.')
    dropgame_menu_command = types.BotCommand(command='dropgame', description='Сбросить партию.')
    cancelshot_menu_command = types.BotCommand(command='cancelshot', description='Отмена последнего удара.')

    bot.set_my_commands([help_menu_command, #руководство
                         newgame_menu_command, #начать новую партию
                         dropgame_menu_command, #сбросить игру
                         cancelshot_menu_command, #отменить последний удар
                         register_player_menu_command #зарегистрироваться
                         ])
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))

    bot.send_message(message.chat.id, "Добро пожаловать. Управление осуществляется с помощью кнопки Menu.")

@bot.message_handler(commands=['newgame']) #обработка команды new_game
def handle_start(message):
    global players, live_players

    if message.from_user.id in live_players:
        bot.reply_to(message, 'Вы уже в игре.')
        return
    else:
        bot.reply_to(message, 'Перешлите сообщение от вашего оппонента боту, чтобы начать игру.')

@bot.message_handler(func=lambda message: message.forward_from is not None) #старт партии и выбор игроков
def choose_opponent(message):
    global players_csv, live_players, active_games
    player_1_id = message.from_user.id
    player_2_id = message.forward_from.id
    players = pd.read_csv(players_csv)
    if player_2_id in live_players:
        bot.reply_to(message, 'Ваш оппонент уже в игре.')
        return
    if not player_1_id in players['id'].unique(): #добавление игроков в базу данных
        players._append({'id': player_1_id, 'first_name': message.from_user.first_name,
                        'username': message.from_user.username}, ignore_index=True)
    if not player_2_id in players['id'].unique():  # добавление игроков в базу данных
        players._append({'id': player_2_id, 'first_name': message.forward_from.first_name,
                        'username': message.forward_from.username}, ignore_index=True)

    players.to_csv(players_csv, index=False)

    markup = types.InlineKeyboardMarkup()

    player_1_first_name = message.from_user.first_name
    player_2_first_name = message.forward_from.first_name

    button_1 = types.InlineKeyboardButton(f'{player_1_first_name}', callback_data='player_1_shot')
    button_2 = types.InlineKeyboardButton(f'{player_2_first_name}', callback_data='player_2_shot')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, f'Партия начинается, кто разбивает?', reply_markup=markup)
    live_players.append([player_1_id, player_2_id])
    game_id = f'{player_1_id}-{datetime.now().date()}'
    active_games[game_id] = {'player_1_id': player_1_id, 'player_2_id': player_2_id,
                             'player_1_first_name': player_1_first_name, 'player_2_first_name': player_2_first_name,
                             'player_1_score': 0, 'player_2_score': 0,
                             'start_time': datetime.now(),
                             'shots': 0,
                             'game_data': {'game_id': [], 'player_id': [], 'timestamp': [], 'shot_type': [],
                                           'shot_score': []},
                             'shooter': ''}

@bot.callback_query_handler(func=lambda call: call.data in ['player_1_shot', 'player_2_shot'])
def make_shot(call):
    global active_games
    game_id = f'{call.from_user.id}-{datetime.now().date()}'
    game_state = active_games[game_id]

    if call.data == 'player_1_shot':
        shooter_name = game_state['player_1_first_name']
        game_state['shooter'] = 1
    elif call.data == 'player_2_shot':
        shooter_name = game_state['player_2_first_name']
        game_state['shooter'] = 2

    shot_data = types.InlineKeyboardMarkup()

    button_ch0 = types.InlineKeyboardButton('Ч0', callback_data='Ч0')
    button_ch1 = types.InlineKeyboardButton('Ч1', callback_data='Ч1')
    button_ch2 = types.InlineKeyboardButton('Ч2', callback_data='Ч2')

    button_s0 = types.InlineKeyboardButton('C0', callback_data='С0')
    button_s1 = types.InlineKeyboardButton('C1', callback_data='С1')
    button_s2 = types.InlineKeyboardButton('C2', callback_data='С2')

    shot_data.add(button_ch0, button_ch1, button_ch2)
    shot_data.add(button_s0, button_s1, button_s2)

    if game_state['shooter'] == 1:
        shooter_name = game_state['player_1_first_name']
    elif game_state['shooter'] == 2:
        shooter_name = game_state['player_2_first_name']

    bot.send_message(call.message.chat.id, f'Введите удар игрока {shooter_name}', reply_markup=shot_data)


@bot.callback_query_handler(func=lambda call: call.data in ['Ч0', 'Ч1', 'Ч2', 'С0', 'С1', 'С2'])
def register_shot(call):
    global active_games
    game_id = f'{call.from_user.id}-{datetime.now().date()}'
    game_state = active_games[game_id]
    game_state['shots'] += 1
    shot_type = call.data[0]
    shot_score = call.data[1]

    if game_state['shooter'] == 1:
        game_state['player_1_score'] += int(shot_score)
    else:
        game_state['player_2_score'] += int(shot_score)


    bot.send_message(call.message.chat.id, f"Удар был записан. {game_state['player_1_first_name']} "
                                           f"{game_state['player_1_score']} - {game_state['player_2_score']} "
                                           f"{game_state['player_2_first_name']}.")

    game_state['game_data']['game_id'].append(game_id)
    if game_state['shooter'] == 1:
        game_state['game_data']['player_id'].append(game_state['player_1_id'])
    elif game_state['shooter'] == 2:
        game_state['game_data']['player_id'].append(game_state['player_2_id'])
    game_state['game_data']['timestamp'].append(datetime.now().strftime("%H:%M:%S"))
    game_state['game_data']['shot_type'].append(shot_type)
    game_state['game_data']['shot_score'].append(shot_score)

    if shot_score == '0':
        if game_state['shooter'] == 1:
            game_state['shooter'] = 2
        else:
            game_state['shooter'] = 1


    if not (game_state['player_1_score'] >= 8 or game_state['player_2_score'] >= 8):
        make_shot(call)
    else:
        game_state['end_time'] = datetime.now()

        time_difference = game_state['end_time'] - game_state['start_time']
        minutes = str(time_difference.total_seconds() // 60).split('.')[0]
        seconds = str(time_difference.total_seconds() % 60).split('.')[0]

        bot.send_message(call.message.chat.id, f"Партия завершена за {minutes}:"
                                               f"{seconds} со счётом"
                                               f" {game_state['player_1_first_name']} - {game_state['player_1_score']},"
                                               f" {game_state['player_2_first_name']} - {game_state['player_2_score']}.")
        player_1_accuracy =
        bot.send_message(call.message.chat.id, f" Количество ударов - {game_state['shots']}."
                                                    f" Точность ")


# @bot.message_handler(commands=['cancelshot'])
# def handle_ctrlz(message):
#     global boxscore, shot_number, shot_score, andrey_score, dima_score
#     boxscore['game_id'] = boxscore['game_id'][:-1]
#     boxscore['shot_number'] = boxscore['shot_number'][:-1]
#     boxscore['player'] = boxscore['player'][:-1]
#     boxscore['timestamp'] = boxscore['timestamp'][:-1]
#     boxscore['shot_type'] = boxscore['shot_type'][:-1]
#     boxscore['shot_score'] = boxscore['shot_score'][:-1]
#     shot_number -= 1
#     if shot_score == '1':
#         if player == 'Андрей':
#             andrey_score -= 1
#         elif player == 'Дима':
#             dima_score -= 1
#     bot.send_message(message.chat.id, f'Последний удар отменён, счёт остается прежним: {andrey_score} - {dima_score}')

bot.polling(none_stop=True)
