from dotenv import load_dotenv
import os
import telegram
from telegram import Update
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import json
import logging

from telegram.utils.helpers import effective_message_type

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


states_database = {}   # Стейт пользователя

users_pd = {}          # Словарь с персональной инфой по пользователям

users_dict = {}        # Словарь с ключем = id пользователя и значением в виде словаря с персональной инфой

pd_agreement_keyboard = [
    [KeyboardButton('Согласен'), KeyboardButton('Не согласен')],
]

phone_number_keyboard = [
    [KeyboardButton('Отправить контакты', request_contact=True)]
]

address_keyboard = [
    [KeyboardButton('Отправить адрес', request_location=True)]
]
pass_keyboard = [['Пропустить']]
main_keyboard = [['Собрать торт', 'Заказы']]
parametr_1_keyboard = [['1 уровень', '2 уровня', '3 уровня']]
parametr_2_keyboard = [['Квадрат', 'Круг', 'Прямоугольник']]
parametr_3_keyboard = [['Без топпинга', 'Белый соус', 'Карамельный сироп'], ['Кленовый сироп', 'Клубничный сироп'], ['Черничный сироп', 'Молочный шоколад']]
parametr_4_keyboard = [['Ежевика', 'Малина', 'Голубика', 'Клубника']]
parametr_5_keyboard = [['Фисташки', 'Безе', 'Фундук', 'Пекан'], ['Маршмеллоу', 'Фундук', 'Марципан', 'Пропустить']]
to_order_keyboard = [['Заказать торт', 'Собрать заново']]


def start(update:Update, context:CallbackContext):
    #добавил строки 50-54, чтобы тестить ветки
    update.message.reply_text('Собрать новый торт или посмотреть заказы?',
                              reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'MAIN_MENU'
    chat_id = update.effective_message.chat_id
    context.bot.send_message(
        chat_id = chat_id,
        text = ' Привет, я бот, созданный для сервиса создания кастомных тортов.'
               ' Чтобы сделать свой заказ, вам нужно согласиться на обработку персональных данных.',
     )
    with open('PD.pdf', 'r') as document:
        context.bot.send_document(
            chat_id = chat_id,
            document = document,
            reply_markup = ReplyKeyboardMarkup(pd_agreement_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
    return 'CHECK_PD_AGREEMENT'


def pd_agreement_handler(update:Update, context:CallbackContext):
    user_reply = update.effective_message.text
    chat_id = update.effective_message.chat_id

    if user_reply == 'Согласен':
        user_last_name = update.effective_message.chat.last_name
        user_first_name = update.effective_message.chat.first_name
        users_pd.update({'Имя': user_first_name, 'Фамилия': user_last_name})
        context.bot.send_message(
        chat_id=chat_id,
        text = f'{user_last_name} {user_first_name}, вы соглались на обработку ваших ПД.\n'
               'Теперь введите пожалуйста ваш номер телефона или отправьте контакт.',
               reply_markup = ReplyKeyboardMarkup(phone_number_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_PHONE_NUMBER'
        

    elif user_reply == 'Не согласен':
        context.bot.send_message(
        chat_id = chat_id,
        text = 'Вы отказались от обработки ваших ПД. \n'
                'Чтобы пользоваться нашим сервисом, вы должны согласится с обработкой персональной информации.',
        reply_markup = ReplyKeyboardMarkup(pd_agreement_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHECK_PD_AGREEMENT'


def phone_number_handler(update:Update, context:CallbackContext):
    user_input = update.effective_message.text    
    chat_id = update.effective_message.chat_id

    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        users_pd.update({'Номер телефона': user_phone_number})
        context.bot.send_message(                     
        chat_id = chat_id,
        text = f'Ваше номер телефона: {user_phone_number}.'
               'Теперь, введите адрес доставки или поделитесь своим местоположением с помощью кнопки ниже.',
        reply_markup=ReplyKeyboardMarkup(address_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_ADDRESS'

    elif user_input.isdigit():
        user_phone_number = user_input
        users_pd.update({'Номер телефона': user_phone_number})     
        context.bot.send_message(                     
            chat_id = chat_id,
            text = f'Ваш номер телефона: {user_input}.\n'
                   'Теперь, введите адрес доставки или поделитесь своим местоположением с помощью кнопки ниже.',
            reply_markup=ReplyKeyboardMarkup(address_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
          
        return 'TAKE_ADDRESS'

    elif not user_input.isdigit():
        context.bot.send_message(
            chat_id = chat_id,
            text = 'Неверный формат номера\n'
                   'Повторите пожалуйста ваш номер телефона'
        )
        return 'TAKE_PHONE_NUMBER'

    
def address_handler(update:Update, context:CallbackContext):
    user_input = update.effective_message.text   
    chat_id = update.effective_message.chat_id
    user_id = update.effective_message.from_user.id

    if update.message.location is not None:
        user_location = update.message.location
        users_pd.update({'Адрес': user_location})
        users_dict.update({user_id: users_pd})
        with open('users_contacts.json', 'w') as file:
            json.dump(users_dict, file)    

    elif user_input:
        users_pd.update({'Адрес': user_input})
        users_dict.update({user_id: users_pd})
        with open('users_contacts.json', 'w') as file:
            json.dump(users_dict, file)


def main_menu(update:Update, context:CallbackContext):
    user_message = update.message.text
    if user_message == 'Собрать торт':
        update.message.reply_text('Количество уровней',
                                  reply_markup=ReplyKeyboardMarkup(parametr_1_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_1'
    elif user_message == 'Заказы':
        update.message.reply_text('Здесь будут Ваши заказы')
        return 'ORDERS'


def parameter_1(update:Update, context:CallbackContext):
    user_message = update.message.text
    update.message.reply_text('Форма',
                              reply_markup=ReplyKeyboardMarkup(parametr_2_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_2'


def parameter_2(update:Update, context:CallbackContext):
    user_message = update.message.text
    update.message.reply_text('Топпинг',
                              reply_markup=ReplyKeyboardMarkup(parametr_3_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_3'


def parameter_3(update:Update, context:CallbackContext):
    user_message = update.message.text
    update.message.reply_text('Ягоды',
                              reply_markup=ReplyKeyboardMarkup(parametr_4_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_4'


def parameter_4(update:Update, context:CallbackContext):
    user_message = update.message.text
    update.message.reply_text('Декор',
                              reply_markup=ReplyKeyboardMarkup(parametr_5_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_5'


def parameter_5(update:Update, context:CallbackContext):
    update.message.reply_text('Надпись',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    chat_id = update.effective_message.chat_id
    return 'PARAMETR_6'


def parameter_6(update:Update, context:CallbackContext):
    update.message.reply_text('Комментарий к заказу',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_7'


def parameter_7(update:Update, context:CallbackContext):
    update.message.reply_text('Данные получателя')
    return 'PARAMETR_8'


def parameter_8(update:Update, context:CallbackContext):
    update.message.reply_text('Дата доставки')
    return 'PARAMETR_9'


def parameter_9(update:Update, context:CallbackContext):
    update.message.reply_text('Время доставки')
    return 'PARAMETR_10'


def parameter_10(update:Update, context:CallbackContext):
    update.message.reply_text('Введите промокод',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'TO_ORDER'


def to_order(update:Update, context:CallbackContext):
    update.message.reply_text('Заказать торт?',
                              reply_markup=ReplyKeyboardMarkup(to_order_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))

    return 'CHECK_TO_ORDER'


def check_to_order(update:Update, context:CallbackContext):
    user_message = update.message.text
    if user_message == 'Заказать торт':
        update.message.reply_text('Торт заказан!')
        return 'START'
    elif user_message == 'Собрать заново':
        return 'START'

def get_orders(update:Update, context:CallbackContext):
    pass


def handle_user_reply(update:Update, context:CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data  
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = states_database.get(chat_id)

    states_functions = {
        'START' : start,
        'CHECK_PD_AGREEMENT' : pd_agreement_handler,
        'TAKE_PHONE_NUMBER' : phone_number_handler,
        'TAKE_ADDRESS' : address_handler,
        'MAIN_MENU': main_menu,
        'PARAMETR_1': parameter_1,
        'PARAMETR_2': parameter_2,
        'PARAMETR_3': parameter_3,
        'PARAMETR_4': parameter_4,
        'PARAMETR_5': parameter_5,
        'PARAMETR_6': parameter_6,
        'PARAMETR_7': parameter_7,
        'PARAMETR_8': parameter_8,
        'PARAMETR_9': parameter_9,
        'PARAMETR_10': parameter_10,
        'ORDERS': get_orders,
        'TO_ORDER': to_order,
        'CHECK_TO_ORDER': check_to_order,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})


def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.location, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    #dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))

    updater.start_polling()
    # with open('users_contacts.json', 'r') as file:
    #     users_json_dict = json.load(file)
    # for id in users_json_dict:
    #     print(users_json_dict[id]['Фамилия'])


if __name__ == '__main__':
    main()

