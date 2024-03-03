import telebot
import csv
from io import StringIO
from datetime import datetime
from telebot import types

bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
player, shot_type, shot_moose, shot_help, shot_score, start, end = '', '', '', '', '', datetime, datetime
game_is_ongoing = 0
game_id = ''
maxim_score = 0
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
    global game_is_ongoing, start, shot_number, game_id, boxscore
    game_is_ongoing = 1
    start = datetime.now()
    shot_number = 0
    boxscore = {'game_id': [], 'shot_number': [], 'timestamp': [], 'player': [],
                'shot_type': [], 'shot_moose': [], 'shot_help': [], 'shot_score': []}
    game_id = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_1 = types.InlineKeyboardButton('Максим', callback_data='Максим')
    button_2 = types.InlineKeyboardButton('Дима', callback_data='Дима')
    markup.add(button_1, button_2)
    bot.send_message(call.message.chat.id, 'Кто разбивает?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Максим', 'Дима'])
def configure_shot(call):
    global player
    player = call.data

    shot_data = types.InlineKeyboardMarkup()

    button_svoi = types.InlineKeyboardButton('Свой', callback_data='Свой')
    button_chuzhoi = types.InlineKeyboardButton('Чужой', callback_data='Чужой')
    button_otigrish = types.InlineKeyboardButton('Отыгрыш', callback_data='Отыгрыш')

    button_moose_yes = types.InlineKeyboardButton('Лось', callback_data='Лось')
    button_moose_no = types.InlineKeyboardButton('Без лося', callback_data='Без лося')

    button_help_yes = types.InlineKeyboardButton('Подставил', callback_data='Подставил')
    button_help_no =  types.InlineKeyboardButton('Не подставил', callback_data='Не подставил')

    button_score_0 = types.InlineKeyboardButton('0', callback_data='0')
    button_score_1 = types.InlineKeyboardButton('1', callback_data='1')
    button_score_2 = types.InlineKeyboardButton('2', callback_data='2')

    shot_data.add(button_svoi, button_chuzhoi, button_otigrish)
    shot_data.add(button_moose_yes, button_moose_no)
    shot_data.add(button_help_yes, button_help_no)
    shot_data.add(button_score_0, button_score_1, button_score_2)

    bot.send_message(call.message.chat.id, f'Введите удар игрока {player}', reply_markup=shot_data)

@bot.callback_query_handler(func=lambda call: call.data in ['Свой', 'Чужой', 'Отыгрыш'])
def shot_type(call):
    global shot_type
    shot_type = call.data

@bot.callback_query_handler(func=lambda call: call.data in ['Лось', 'Без лося'])
def shot_moose(call):
    global shot_moose
    shot_moose = call.data

@bot.callback_query_handler(func=lambda call: call.data in ['Подставил', 'Не подставил'])
def shot_help(call):
    global shot_help
    shot_help = call.data


@bot.callback_query_handler(func=lambda call: call.data in ['0', '1', '2'])
def shot_score(call):
    global shot_score, player, dima_score, maxim_score, start, end, game_is_ongoing, shot_number, game_id, boxscore
    shot_score = call.data

    shot_number += 1

    if player == 'Максим':
        maxim_score += int(shot_score)
    else:
        dima_score += int(shot_score)

    bot.send_message(call.message.chat.id, f'Удар был записан. Максим {maxim_score} - {dima_score} Дима.')
    if shot_score == '0':
        if player == 'Максим':
            player = 'Дима'
        else:
            player = 'Максим'

    call.data = player

    shot_type_cipher = {'Свой': 0, 'Чужой': 1, 'Отыгрыш': 2}
    shot_moose_cipher = {'Лось': 1, 'Без лося': 0}
    shot_help_cipher = {'Подставил': 1, 'Не подставил': 0}

    boxscore['game_id'].append(game_id)
    boxscore['shot_number'].append(shot_number)
    boxscore['player'].append(player)
    boxscore['timestamp'].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    boxscore['shot_type'].append(shot_type_cipher[shot_type])
    boxscore['shot_moose'].append(shot_moose_cipher[shot_moose])
    boxscore['shot_help'].append(shot_help_cipher[shot_help])
    boxscore['shot_score'].append(shot_score)

    if not (maxim_score >= 8 or dima_score >= 8):
        configure_shot(call)
    else:
        end = datetime.now()

        time_difference = end - start
        minutes = time_difference.total_seconds() // 60
        seconds = time_difference.total_seconds() % 60

        bot.send_message(call.message.chat.id, f'Партия завершена за {str(minutes).split(".")[0]}:'
                                               f'{str(seconds).split(".")[0]} со счётом'
                                               f' Максим - {maxim_score}, Дима - {dima_score}.')
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
