import telebot
import csv
from io import StringIO
from datetime import datetime
from telebot import types
import os

bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
players = "D:\Projects\nerdiard\players.csv" #список всех пользователей бота
live_players = "D:\Projects\nerdiard\live_players.csv" #список играющих в данных момент пользователей
data = "D:\Projects\nerdiard\data.csv" #данные


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
    global players, live_players
    player_1 = message.from_user.id
    player_2 = message.forward_from.id

    if player_2 in live_players:
        bot.reply_to(message, 'Ваш оппонент уже в игре.')
        return
    if not player_1 in [player['id'] for player in players]:
        players.append({'name': message.from_user.first_name, 'id': player_1})
    if not player_2 in [player['id'] for player in players]:
        players.append({'name': message.forward_from.first_name, 'id': player_2})

    markup = types.InlineKeyboardMarkup()

    player_1_name = next((player['name'] for player in players if player['id'] == player_1), None)
    player_2_name = next((player['name'] for player in players if player['id'] == player_2), None)

    button_1 = types.InlineKeyboardButton(f'{player_1_name}', callback_data='show_shot')
    button_2 = types.InlineKeyboardButton(f'{player_2_name}', callback_data='show_shot')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, f'Партия начинается, кто разбивает?', reply_markup=markup)
    live_players.append([player_1, player_2])



@bot.callback_query_handler(func=lambda call: call.data == 'show_shot')
def new_game(call):
    global game_is_ongoing, start, shot_number, game_id, boxscore, andrey_score, dima_score
    game_is_ongoing = 1
    start = datetime.now()
    shot_number = 0
    andrey_score, dima_score = 0, 0
    boxscore = {'game_id': [], 'shot_number': [], 'timestamp': [], 'player': [],
                'shot_type': [], 'shot_score': []}
    game_id = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_1 = types.InlineKeyboardButton('Андрей', callback_data='Андрей')
    button_2 = types.InlineKeyboardButton('Дима', callback_data='Дима')
    markup.add(button_1, button_2)
    bot.send_message(call.message.chat.id, 'Кто разбивает?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Андрей', 'Дима'])
def configure_shot(call):
    global player
    player = call.data

    shot_data = types.InlineKeyboardMarkup()

    button_ch0 = types.InlineKeyboardButton('Ч0', callback_data='Ч0')
    button_ch1 = types.InlineKeyboardButton('Ч1', callback_data='Ч1')
    button_ch2 = types.InlineKeyboardButton('Ч2', callback_data='Ч2')

    button_s0 = types.InlineKeyboardButton('C0', callback_data='С0')
    button_s1 = types.InlineKeyboardButton('C1', callback_data='С1')
    button_s2 = types.InlineKeyboardButton('C2', callback_data='С2')

    shot_data.add(button_ch0, button_ch1, button_ch2)
    shot_data.add(button_s0, button_s1, button_s2)

    bot.send_message(call.message.chat.id, f'Введите удар игрока {player}', reply_markup=shot_data)


@bot.callback_query_handler(func=lambda call: call.data in ['Ч0', 'Ч1', 'Ч2', 'С0', 'С1', 'С2'])
def shot(call):
    global shot_type, shot_score, player, andrey_score, dima_score, shot_number, start, end, game_is_ongoing
    shot_type = call.data[0]
    shot_score = call.data[1]

    shot_number += 1
    if player == 'Андрей':
        andrey_score += int(shot_score)
    else:
        dima_score += int(shot_score)

    bot.send_message(call.message.chat.id, f'Удар был записан. Андрей {andrey_score} - {dima_score} Дима.')
    if shot_score == '0':
        if player == 'Андрей':
            player = 'Дима'
        else:
            player = 'Андрей'

    call.data = player

    boxscore['game_id'].append(game_id)
    boxscore['shot_number'].append(shot_number)
    boxscore['player'].append(player)
    boxscore['timestamp'].append(datetime.now().strftime("%H:%M:%S"))
    boxscore['shot_type'].append(shot_type)
    boxscore['shot_score'].append(shot_score)

    if not (andrey_score >= 8 or dima_score >= 8):
        configure_shot(call)
    else:
        end = datetime.now()

        time_difference = end - start
        minutes = time_difference.total_seconds() // 60
        seconds = time_difference.total_seconds() % 60

        bot.send_message(call.message.chat.id, f'Партия завершена за {str(minutes).split(".")[0]}:'
                                               f'{str(seconds).split(".")[0]} со счётом'
                                               f' Максим - {andrey_score}, Дима - {dima_score}.'
                                               f' Количество ударов - {shot_number}.')
        game_is_ongoing = 0

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        # Write the header
        csv_writer.writerow(boxscore.keys())

        for row in zip(*boxscore.values()):
            csv_writer.writerow(row)

        csv_data.seek(0)

        bot.send_document(call.message.chat.id, csv_data)

        new_game(call)

# @bot.message_handler(commands=['ctrlz'])
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
