import telebot
import csv
from io import StringIO
from datetime import datetime
from telebot import types

bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
player, shot_type, shot_score, start, end = '', '', '', datetime, datetime
game_is_ongoing = 0
game_id = ''
andrey_score = 0
dima_score = 0
shot_number = 0
boxscore = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    # Create an inline keyboard with the new_game button
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Начать новую партию.", callback_data="new_game")
    markup.add(button)
    bot.send_message(message.chat.id, "Добро пожаловать в бот. Нажмите кнопку ниже чтобы начать новую партию.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'new_game')
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

    button_s0 = types.InlineKeyboardButton('C0', callback_data='C0')
    button_s1 = types.InlineKeyboardButton('C1', callback_data='C1')
    button_s2 = types.InlineKeyboardButton('C2', callback_data='C2')

    shot_data.add(button_ch0, button_ch1, button_ch2)
    shot_data.add(button_s0, button_s1, button_s2)

    bot.send_message(call.message.chat.id, f'Введите удар игрока {player}', reply_markup=shot_data)

@bot.callback_query_handler(func=lambda call: call.data in ['Ч0', 'Ч1', 'Ч2', 'С0', 'С1','С2'])
def shot(call):
    global shot_type, shot_score, player, andrey_score, dima_score, shot_number
    shot_type = int(call.data[1])
    shot_score = int(call.data[1])

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


bot.polling(none_stop=True)
