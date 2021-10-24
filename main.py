from dotenv import load_dotenv
import os
import telegram
from telegram import Update
from telegram import chat
from telegram import replymarkup
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import json
import logging


states_database = {}   

users_pd = {}          

json_contacts = {}

order = {'Статус заказа':'Заявка обрабатывается'}

price = {
    '1 уровень': 400,
    '2 уровня': 750,
    '3 уровня': 1100,
    'Квадрат': 600,
    'Круг': 400,
    'Прямоугольник': 600,
    'Без топпинга': 0,
    'Белый соус': 200,
    'Карамельный сироп': 180,
    'Кленовый сироп': 200,
    'Клубничный сироп': 300,
    'Черничный сироп': 350,
    'Молочный шоколад': 200,
    'Ежевика': 400,
    'Малина': 300,
    'Голубика': 450,
    'Клубника': 500,
    'Фисташки': 300,
    'Безе': 400,
    'Фундук': 350,
    'Пекан': 300,
    'Маршмеллоу': 200,
    'Марципан': 300,
    'Надпись': 500
}


pd_agreement_keyboard = [
    [KeyboardButton('Согласен'), KeyboardButton('Не согласен')],
]

phone_number_keyboard = [
    [KeyboardButton('Отправить контакты', request_contact=True)]
]

address_keyboard = [
    [KeyboardButton('Отправить адрес', request_location=True)]
]
ok_keyboard = [['Выбрать по умолчанию']]
pass_keyboard = [['Пропустить']]
date_keyboard = [['В течение 24 часов']]
main_keyboard = [
    [KeyboardButton('Собрать торт'), KeyboardButton('Заказы')]
]
parametr_1_keyboard = [['1 уровень', '2 уровня', '3 уровня']]
parametr_2_keyboard = [['Квадрат', 'Круг', 'Прямоугольник']]
parametr_3_keyboard = [['Без топпинга', 'Белый соус', 'Карамельный сироп'], ['Кленовый сироп', 'Клубничный сироп'], ['Черничный сироп', 'Молочный шоколад']]
parametr_4_keyboard = [['Ежевика', 'Малина', 'Голубика', 'Клубника'], ['Пропустить']]
parametr_5_keyboard = [['Фисташки', 'Безе', 'Фундук', 'Пекан'], ['Маршмеллоу', 'Фундук', 'Марципан', 'Пропустить']]
to_order_keyboard = [['Заказать торт', 'Собрать заново']]
user_orders_keyboard = [['Главное меню']]


def start(update:Update, context:CallbackContext):
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
                   'Теперь, введите адрес доставки или поделитесь своим местоположением с помощью кнопки ниже.'
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
    user_id = update.message.from_user.id

    # if update.message.location is not None:
    #     user_location = update.message.location
    #     users_pd.update({'Адрес': user_location})
    #     users_dict.update({user_id: users_pd})
    #     with open('users_contacts.json', 'a', encoding='utf-8') as file:
    #         json.dump(users_dict, file, ensure_ascii=False)    
    
    if user_input:
        users_dict = {} 
        users_pd.update({'Адрес': user_input})
        users_dict[user_id] = users_pd
        json_contacts.update(users_dict)
        with open('users_contacts.json', 'w', encoding='utf-8') as file:
            json.dump(json_contacts, file, ensure_ascii=False)
        context.bot.send_message(
            chat_id=chat_id,
            text = 'Предоставленная информация сохранена в базе, можете приступать к заказу'
        )
        update.message.reply_text('Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return 'MAIN_MENU'


def main_menu_handler(update:Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text = 'Вы уже зарегистрированы, вы молодец'
    )
    update.message.reply_text(
        'Собрать новый торт или посмотреть заказы?',
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU' 


def main_menu(update:Update, context: CallbackContext):
    user_message = update.effective_message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if user_message == 'Собрать торт':
        update.message.reply_text('Количество уровней',
                                  reply_markup=ReplyKeyboardMarkup(parametr_1_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_1'

    elif user_message == 'Заказы':
        with open('orders.json', 'r', encoding='utf-8') as file:
            orders_info = json.load(file)
        if str(user_id) in orders_info:
            chat_id = update.message.chat_id 
            orders_list = orders_info[str(user_id)]
            for order in orders_list:
                text = create_order_text_for_user(order)
                new_keyboard = create_keyboard_for_user_order(order)
                if new_keyboard not in user_orders_keyboard:
                    user_orders_keyboard.append(new_keyboard)
                context.bot.send_message(
                    chat_id=chat_id,
                    text = text,
                    reply_markup = ReplyKeyboardMarkup(user_orders_keyboard, resize_keyboard=True, one_time_keyboard=True)
                )
            return 'FILTER_THE_ORDERS'
        else:
            context.bot.send_message(
                chat_id = chat_id,
                text = 'У вас нет ни одного заказа',
                reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
            )
            return 'MAIN_MENU'


def get_filtered_oreders(update:Update, context:CallbackContext):
    user_reply = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    status_list = ['Заявка обрабатывается', 'Готовим ваш торт', 'Торт в пути', 'Торт у вас']
    with open('orders.json', 'r', encoding='utf-8') as file:
        orders_info = json.load(file)
    orders_list = orders_info[str(user_id)]
    if user_reply:    
        if user_reply == 'Главное меню':
            context.bot.send_message(
                    chat_id = chat_id,
                    text = 'Главное меню',
                    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
                ) 
            return 'MAIN_MENU'
        elif user_reply in status_list:
            for order in orders_list:
                if order['Статус заказа'] == user_reply:
                    text = create_order_text_for_user(order)
                    context.bot.send_message(
                        chat_id = chat_id,
                        text = text,
                        reply_markup = ReplyKeyboardMarkup(user_orders_keyboard, resize_keyboard=True, one_time_keyboard=True)
                    )
            return 'FILTER_THE_ORDERS'
        else:
            context.bot.send_message(
                        chat_id = chat_id,
                        text = 'Я вас не понимаю.\n'
                                'Пожалуйста, выберите статус из списка ниже.',
                        reply_markup = ReplyKeyboardMarkup(user_orders_keyboard, resize_keyboard=True, one_time_keyboard=True)
                    )
            return 'FILTER_THE_ORDERS'


    
def create_order_text_for_user(order):
    text = ''
    for key,value in order.items():
        if order[key] != None: 
            text += f'{key}: {value}\n'
    return text


def create_keyboard_for_user_order(order):
    order_status = order['Статус заказа']
    orders_user_new_keyboard = [order_status]
    return orders_user_new_keyboard


def parameter_1(update:Update, context:CallbackContext):
    user = update.message.from_user
    user_input = update.effective_message.text
    order.update({'Номер заказа': user.id})
    order.update({'Количество уровней': user_input})
    update.message.reply_text('Форма',
                              reply_markup=ReplyKeyboardMarkup(parametr_2_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_2'


def parameter_2(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    order.update({'Форма': user_input})
    user_input = update.effective_message.text
    update.message.reply_text('Топпинг',
                              reply_markup=ReplyKeyboardMarkup(parametr_3_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_3'


def parameter_3(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    order.update({'Топпинг': user_input})
    update.message.reply_text('Ягоды',
                              reply_markup=ReplyKeyboardMarkup(parametr_4_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_4'


def parameter_4(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    if user_input != 'Пропустить':
        order.update({'Ягоды': user_input})
    update.message.reply_text('Декор',
                              reply_markup=ReplyKeyboardMarkup(parametr_5_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_5'


def parameter_5(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    if user_input != 'Пропустить':
        order.update({'Декор': user_input})
    update.message.reply_text('Надпись',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_6'


def parameter_6(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    if user_input != 'Пропустить':
        order.update({'Надпись': user_input})
    update.message.reply_text('Комментарий к заказу',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_7'


def parameter_7(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    user_id = update.message.from_user.id

    if user_input != 'Пропустить':
        order.update({'Комментарий к заказу': user_input})

    with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
        data = json.load(read_file)[str(user_id)]
        contact = '{} {} {}'.format(data['Имя'], data['Фамилия'], data['Номер телефона'])
        order.update({'Получатель': contact})
    update.message.reply_text(
        text = f'Контакты по умолчанию: {contact}\n'
                'Выберите контакты по умолчанию или введите новые в формате: имя фамилия, номер телефона',
        reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )                                               
    return 'PARAMETR_7_1'


def parametr_7_1(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    user_id = update.message.from_user.id

    if user_input != 'Выбрать по умолчанию':
        order.update({'Получатель': user_input})
    
    with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
        data = json.load(read_file)[str(user_id)]
        address = data['Адрес']
        order.update({'Адрес': address})
    update.message.reply_text(f'Адрес по умолчанию: {address}\n'
                               'Выберите адрес по умолчанию или введите другой',
                                reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'PARAMETR_8'


def parameter_8(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    if user_input != 'Выбрать по умолчанию':
        order.update({'Адрес': user_input})
    update.message.reply_text('Дата доставки в формате "dd-mm". Например: 23.10.\n Введите дату или нажмите кнопку ниже при срочном заказе, при этом:\n'
                              ' - точное время будет сообщено по телефону сразу после готовности заказа\n'
                              ' - стоимость заказа будет увеличена на 20%',
                              reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_9'

import re


def parameter_9(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    order.update({'Дата': user_input})

    if user_input == 'В течение 24 часов':
        update.message.reply_text('Введите промокод',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'TO_ORDER'

    if not (bool(re.search(rf'^(\d\d).(\d\d)$', user_input))):
        update.message.reply_text('Некорректная дата. Введите дату в формате "dd.mm". Например: 23.10',
                                  reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_8'

    update.message.reply_text('Время доставки')
    return 'PARAMETR_10'


def parameter_10(update:Update, context:CallbackContext):
    # здесь надо проверить валидность времени
    update.message.reply_text('Введите промокод',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'TO_ORDER'


def to_order(update:Update, context:CallbackContext):
    update.message.reply_text('Заказать торт?',
                              reply_markup=ReplyKeyboardMarkup(to_order_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    total_price = 0
    for i in order.values():
        try:
            total_price += price.get(i)
        except:
            pass
    if order['Дата'] == 'В течение 24 часов':
        total_price = int(total_price * 1.2)

    user_input_promo = update.effective_message.text
    user_id = update.message.from_user.id
    order.update({'Стоимость': total_price})

    # orders.append(order)
    # orders_dict[user_id] = orders
    # json_orders.update(orders_dict)
    # print(json_orders)

    update.message.reply_text('Стоимость торта составит {} рублей'.format(total_price))
    return 'CHECK_TO_ORDER'


def check_to_order(update:Update, context:CallbackContext):
    global order
    user_message = update.message.text
    user_id = update.message.from_user.id

    orders = []
    json_orders = {}
    with open('orders.json', 'r', encoding='utf-8') as file:
        latest_orders = json.load(file)
    json_orders.update(latest_orders)

    if str(user_id) in latest_orders:
        orders = latest_orders[str(user_id)]
        del json_orders[str(user_id)]  
        orders.append(order)
        json_orders[user_id] = orders
    else:
        orders.append(order)
        json_orders.update({user_id: orders})

    if user_message == 'Заказать торт':
        with open('orders.json', 'w', encoding='utf-8') as file:
            json.dump(json_orders, file, ensure_ascii=False)
        update.message.reply_text(
            'Торт заказан!',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'

    elif user_message == 'Собрать заново':
        order = {'Статус заказа':'Заявка обрабатывается'}
        update.message.reply_text(
            'Вы перенаправлены в Главное меню для повторного сбора торта',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'


def handle_user_reply(update:Update, context:CallbackContext):
    with open('users_contacts.json', 'r', encoding='utf-8') as file:
        users_json_dict = json.load(file)
        json_contacts.update(users_json_dict)

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        
    elif update.callback_query:
        user_reply = update.callback_query.data  
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        if str(user_id) in users_json_dict:
            user_state = 'MAIN_MENU_HANDLER'       
        else:
            user_state = 'START'
        
    else:
        user_state = states_database.get(chat_id)

    states_functions = {
        'START' : start,
        'CHECK_PD_AGREEMENT' : pd_agreement_handler,
        'TAKE_PHONE_NUMBER' : phone_number_handler,
        'TAKE_ADDRESS' : address_handler,
        'MAIN_MENU_HANDLER' : main_menu_handler,
        'MAIN_MENU': main_menu,
        'PARAMETR_1': parameter_1,
        'PARAMETR_2': parameter_2,
        'PARAMETR_3': parameter_3,
        'PARAMETR_4': parameter_4,
        'PARAMETR_5': parameter_5,
        'PARAMETR_6': parameter_6,
        'PARAMETR_7': parameter_7,
        'PARAMETR_7_1':parametr_7_1,
        'PARAMETR_8': parameter_8,
        'PARAMETR_9': parameter_9,
        'PARAMETR_10': parameter_10,
        'TO_ORDER': to_order,
        'CHECK_TO_ORDER': check_to_order,
        'FILTER_THE_ORDERS': get_filtered_oreders,
    }
    
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})


def main():
    load_dotenv()
    logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.location, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))

    updater.start_polling()

if __name__ == '__main__':
    main()

