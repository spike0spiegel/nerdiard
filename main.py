import telebot
from telebot import types


bot = telebot.TeleBot('6850191251:AAH1OLlxBoCd09ZSzIojE5h04DR0DawvwEY')
player = ''


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
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_1 = types.InlineKeyboardButton('Максим', callback_data='Максим')
    button_2 = types.InlineKeyboardButton('Дима', callback_data='Дима')
    markup.add(button_1, button_2)
    bot.send_message(call.message.chat.id, 'Кто разбивает?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Максим', 'Дима'])
def shot(call):
    global player
    player = call.data

    shot_data = types.InlineKeyboardMarkup()

    button_svoi = types.InlineKeyboardButton('Свой', callback_data='Свой')
    button_chuzhoi = types.InlineKeyboardButton('Чужой', callback_data='Чужой')
    button_otigrish = types.InlineKeyboardButton('Отыгрыш', callback_data='Отыгрыш')
    shot_type = call.data

    button_moose_yes = types.InlineKeyboardButton('Лось', callback_data='Лось')
    button_moose_no = types.InlineKeyboardButton('Без лося', callback_data='Без лося')
    shot_moose = call.data

    button_help_yes = types.InlineKeyboardButton('Подставил', callback_data='Подставил')
    button_help_no =  types.InlineKeyboardButton('Не подставил', callback_data='Не подставил')
    shot_help = call.data

    button_score_0 = types.InlineKeyboardButton('0', callback_data='0')
    button_score_1 = types.InlineKeyboardButton('1', callback_data='1')
    button_score_2 = types.InlineKeyboardButton('2', callback_data='2')
    shot_score = call.data

    shot_data.add(button_svoi, button_chuzhoi, button_otigrish)
    shot_data.add(button_moose_yes, button_moose_no)
    shot_data.add(button_help_yes, button_help_no)
    shot_data.add(button_score_0, )

    bot.send_message(call.message.chat.id, f'Введите данные удара игрока {player}', reply_markup=shot_data)

bot.polling(none_stop=True)
