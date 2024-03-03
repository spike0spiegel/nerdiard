import telebot
from telebot import types


bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
player, shot_type, shot_moose, shot_help, shot_score = '', '', '', '', ''
game_is_ongoing = 0

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
    global game_is_ongoing
    game_is_ongoing = 1
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
    if call.data in ['Свой', 'Чужой', 'Отыгрыш']:
        global shot_type
        shot_type = '1'

    button_moose_yes = types.InlineKeyboardButton('Лось', callback_data='Лось')
    button_moose_no = types.InlineKeyboardButton('Без лося', callback_data='Без лося')
    if call.data in ['Лось', 'Без лося']:
        global shot_moose
        shot_moose = call.data

    button_help_yes = types.InlineKeyboardButton('Подставил', callback_data='Подставил')
    button_help_no =  types.InlineKeyboardButton('Не подставил', callback_data='Не подставил')
    if call.data in ['Подставил', 'Не подставил']:
        global shot_help
        shot_help = call.data

    button_score_0 = types.InlineKeyboardButton('0', callback_data='0')
    button_score_1 = types.InlineKeyboardButton('1', callback_data='1')
    button_score_2 = types.InlineKeyboardButton('2', callback_data='2')
    if call.data in ['0', '1', '2']:
        global shot_score
        shot_score = call.data

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
    global shot_score, player
    shot_score = call.data

    bot.send_message(call.message.chat.id, f'Удар был записан.')
    if shot_score == '0':
        if player == 'Максим':
            player = 'Дима'
        else:
            player = 'Максим'

    call.data = player
    configure_shot(call)

bot.polling(none_stop=True)
