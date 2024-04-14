import telebot
from datetime import datetime
from telebot import types
import pandas as pd
import csv

bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработка команды start, создание кнопки меню и приветственное сообщение."""

    #help_menu_command = types.BotCommand(command='help', description='Руководство.')
    newgame_menu_command = types.BotCommand(command='newgame', description='Начать новую партию.')
    myshooting_menu_command = types.BotCommand(command='myshooting', description='Посмотреть статистику моих ударов.')
    dropgame_menu_command = types.BotCommand(command='dropgame', description='Сбросить партию.')
    cancelshot_menu_command = types.BotCommand(command='cancelshot', description='Отмена последнего удара.')

    bot.set_my_commands([#help_menu_command, #руководство
                         newgame_menu_command, #начать новую партию
                         dropgame_menu_command, #сбросить игру
                         cancelshot_menu_command, #отменить последний удар
                         myshooting_menu_command #точность ударов
                         ])
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))

    bot.send_message(message.chat.id, "Добро пожаловать. Управление осуществляется с помощью кнопки Menu.")

@bot.message_handler(commands=['newgame'])
def handle_newgame(message):
    """Обработка команды newgame. Если тот, кто отправляет эту команду, уже в игре, то будет написано,
    что он уже в игре. Если нет, то пользователю предложат переслать сообщение от противника боту."""
    from sql_functions import check_active_player
    if check_active_player(message.from_user.id):
        bot.reply_to(message, 'Вы уже в игре.')
        return
    else:
        bot.reply_to(message, 'Перешлите любое сообщение от вашего оппонента боту, чтобы начать игру.')

@bot.message_handler(func=lambda message: message.forward_from is not None) #старт партии и выбор игроков
def choose_opponent(message):
    from sql_functions import switch_active_player, create_live_game, get_live_game_id
    player_1_id = message.from_user.id
    player_2_id = message.forward_from.id
    from sql_functions import check_active_player
    if check_active_player(player_2_id):
        bot.reply_to(message, 'Ваш оппонент уже в игре.')
        return
    switch_active_player(player_1_id)
    switch_active_player(player_2_id)

    markup = types.InlineKeyboardMarkup()

    player_1_first_name = message.from_user.first_name
    player_2_first_name = message.forward_from.first_name

    button_1 = types.InlineKeyboardButton(f'{player_1_first_name}', callback_data='player_1_shot')
    button_2 = types.InlineKeyboardButton(f'{player_2_first_name}', callback_data='player_2_shot')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, f'Партия начинается, кто разбивает?', reply_markup=markup)

    create_live_game(player_1_id, player_2_id, player_1_first_name, player_2_first_name)

@bot.callback_query_handler(func=lambda call: call.data in ['player_1_shot', 'player_2_shot'])
def configure_shot(call):
    from sql_functions import get_live_game_id, set_shooter
    game_id = get_live_game_id(call.from_user.id)
    if not game_id:
        return

    shooter_id = (game_id.strip('_')[0], game_id.strip('_')[1])[call.data == 'player_2_shot']
    shooter_name =
    set_shooter(game_id, shooter_name)

    shot_data = types.InlineKeyboardMarkup()

    button_ch0 = types.InlineKeyboardButton('Ч0', callback_data='Ч0')
    button_ch1 = types.InlineKeyboardButton('Ч1', callback_data='Ч1')
    button_ch2 = types.InlineKeyboardButton('Ч2', callback_data='Ч2')

    button_s0 = types.InlineKeyboardButton('C0', callback_data='С0')
    button_s1 = types.InlineKeyboardButton('C1', callback_data='С1')
    button_s2 = types.InlineKeyboardButton('C2', callback_data='С2')
    button_o = types.InlineKeyboardButton('O', callback_data='O')

    shot_data.add(button_ch0, button_ch1, button_ch2)
    shot_data.add(button_s0, button_s1, button_s2)
    shot_data.add(button_o)

    bot.send_message(call.message.chat.id, f'Введите удар игрока {shooter_name}', reply_markup=shot_data)


@bot.callback_query_handler(func=lambda call: call.data in ['Ч0', 'Ч1', 'Ч2', 'С0', 'С1', 'С2', 'O'])
def register_shot(call):
    from sql_functions import get_live_game_id, switch_shooter, register_shot
    game_id = get_live_game_id(call.from_user.id)
    if not game_id:
        return
    shot_type = call.data[0]
    shot_score = call.data[1]
    register_shot(game_id, shot_type,shot_score,)
    bot.send_message(call.message.chat.id, f"Удар был записан. ")

    if shot_score == '0':



    if not (game_state['player_1_score'] >= 8 or game_state['player_2_score'] >= 8):
        configure_shot(call)
    else:
        game_state['end_time'] = datetime.now()

        for row in game_state['game_data']:
            row[0] += str(game_state['end_time'])[-5:]

        time_difference = game_state['end_time'] - game_state['start_time']
        minutes = str(time_difference.total_seconds() // 60).split('.')[0]
        seconds = str(time_difference.total_seconds() % 60).split('.')[0]

        bot.send_message(call.message.chat.id, f"Партия завершена за {minutes}:"
                                               f"{seconds} со счётом"
                                               f" {game_state['player_1_first_name']} - {game_state['player_1_score']} :"
                                               f" {game_state['player_2_score']} - {game_state['player_2_first_name']}.")

        player_1_count, player_2_count, player_1_scored, player_2_scored = 0, 0, 0, 0
        for row in game_state['game_data']:
            if row[2] == game_state['player_1_id']:
                if row[4] == '0':
                    player_1_count += 1
                else:
                    player_1_count += 1
                    player_1_scored += 1
            elif row[2] == game_state['player_2_id']:
                if row[4] == '0':
                    player_2_count += 1
                else:
                    player_2_count += 1
                    player_2_scored += 1
        player_1_acc = str(100 * player_1_scored / player_1_count)[:5] + '%'
        player_2_acc = str(100 * player_2_scored / player_2_count)[:5] + '%'


        bot.send_message(call.message.chat.id, f" Количество ударов - {game_state['shots']}."
                                                    f" Точность {game_state['player_1_first_name']} -"
                                               f" {player_1_acc}"
                                                    f" Точность {game_state['player_2_first_name']} - "
                                               f"{player_2_acc}")

        with open(data, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(game_state['game_data'])

        del game_state
        del active_games[game_id]



@bot.message_handler(commands=['cancelshot'])
def handle_cancelshot(message):
    global active_games, data
    game_id = f'{message.from_user.id}-{datetime.now().date()}'
    try:
        game_state = active_games[game_id]
    except:
        return

    deleted_row = game_state['game_data'].pop(-1)
    deleted_score = deleted_row[4]
    deleted_player_id = deleted_row[2]
    game_state['shots'] -= 1
    if deleted_player_id == game_state['player_1_id']:
        game_state['player_1_score'] -= int(deleted_score)
    elif deleted_player_id == game_state['player_2_id']:
        game_state['player_2_score'] -= int(deleted_score)

    if deleted_score == 1:
        if game_state['shooter'] == 1:
            game_state['shooter'] = 2
            callback_data = 'player_2_shot'
        else:
            game_state['shooter'] = 1
            callback_data = 'player_1_shot'
    else:
        if game_state['shooter'] == 1:
            callback_data = 'player_1_shot'
        else:
            callback_data = 'player_2_shot'

    markup = types.InlineKeyboardMarkup()

    button_1 = types.InlineKeyboardButton(f'Подтвердить.', callback_data=callback_data)
    markup.add(button_1)
    bot.send_message(message.chat.id, f"Удар отменён, счёт прежний {game_state['player_1_first_name']} - "
                                        f"{game_state['player_1_score']} :"
                                        f" {game_state['player_2_score']} - {game_state['player_2_first_name']}.",
                     reply_markup=markup)


@bot.message_handler(commands=['dropgame'])
def handle_dropgame(message):
    global active_games, data
    game_id = f'{message.from_user.id}-{datetime.now().date()}'
    try:
        game_state = active_games[game_id]
    except:
        return

    del game_state
    del active_games[game_id]

    bot.send_message(message.chat.id, 'Партия остановлена.')


@bot.message_handler(commands=['myshooting']) #обработка команды new_game
def handle_shooting(message):
    from sql_functions import get_player_accuracy
    global data
    players = pd.read_csv(data)['player_id'].unique()
    if message.from_user.id not in players:
        bot.reply_to(message, 'Вы ещё не сыграли ни одной партии.')
    else:
        bot.reply_to(message,   f"Общая точность - {get_player_accuracy(message.from_user.id)}.\n")

bot.polling(none_stop=True)
