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
from datetime import datetime, timedelta


states_database = {}
users_pd = {}
json_contacts = {}
order = {'Статус заказа': 'Заявка обрабатывается'}
promocodes = ['ТОРТ']

price = {
    '1 уровень': 400,
    '2 уровня': 750,
    '3 уровня': 1100,
    'Квадрат': 600,
    'Круг': 400,
    'Прямоугольник': 1000,
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
    'Марципан': 280,
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
ok_keyboard = [['Выбрать по умолчанию'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
pass_keyboard = [['Пропустить'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
date_keyboard = [['В ближайшее время'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
main_keyboard = [
    [KeyboardButton('Собрать торт'), KeyboardButton('Заказы')]
]

parametr_1_keyboard = [['1 уровень', '2 уровня', '3 уровня'], ['ГЛАВНОЕ МЕНЮ']]
parametr_2_keyboard = [['Квадрат', 'Круг', 'Прямоугольник'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
parametr_3_keyboard = [['Без топпинга', 'Белый соус', 'Карамельный сироп'], ['Кленовый сироп', 'Клубничный сироп'],
                       ['Черничный сироп', 'Молочный шоколад'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
parametr_4_keyboard = [['Ежевика', 'Малина', 'Голубика'], ['Клубника', 'Пропустить'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
parametr_5_keyboard = [['Фисташки', 'Безе', 'Пекан'], ['Маршмеллоу', 'Фундук', 'Марципан'], ['Пропустить'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
to_order_keyboard = [['Заказать торт'], ['НАЗАД', 'ГЛАВНОЕ МЕНЮ']]
user_orders_keyboard = [['Главное меню']]

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text=' Привет, я бот, созданный для сервиса создания кастомных тортов.'
             ' Чтобы сделать свой заказ, вам нужно согласиться на обработку персональных данных.',
    )
    with open('PD.pdf', 'r') as document:
        context.bot.send_document(
            chat_id=chat_id,
            document=document,
            reply_markup=ReplyKeyboardMarkup(pd_agreement_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
    return 'CHECK_PD_AGREEMENT'


def pd_agreement_handler(update: Update, context: CallbackContext):
    user_reply = update.effective_message.text
    chat_id = update.effective_message.chat_id
    if user_reply == 'Согласен':
        user_last_name = update.effective_message.chat.last_name
        user_first_name = update.effective_message.chat.first_name
        users_pd.update({'Имя': user_first_name, 'Фамилия': user_last_name})
        context.bot.send_message(
            chat_id=chat_id,
            text=f'{user_last_name} {user_first_name}, вы соглались на обработку ваших ПД.\n'
                 'Теперь введите пожалуйста ваш номер телефона или отправьте контакт.',
            reply_markup=ReplyKeyboardMarkup(phone_number_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_PHONE_NUMBER'

    elif user_reply == 'Не согласен':
        context.bot.send_message(
            chat_id=chat_id,
            text='Вы отказались от обработки ваших ПД. \n'
                 'Чтобы пользоваться нашим сервисом, вы должны согласится с обработкой персональной информации.',
            reply_markup=ReplyKeyboardMarkup(pd_agreement_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'CHECK_PD_AGREEMENT'


def phone_number_handler(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    chat_id = update.effective_message.chat_id
    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        users_pd.update({'Номер телефона': user_phone_number})
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Ваше номер телефона: {user_phone_number}.'
                 'Теперь, введите адрес доставки или поделитесь своим местоположением с помощью кнопки ниже.',
            reply_markup=ReplyKeyboardMarkup(address_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_ADDRESS'
    elif user_input.isdigit():
        user_phone_number = user_input
        users_pd.update({'Номер телефона': user_phone_number})
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Ваш номер телефона: {user_input}.\n'
                 'Теперь, введите адрес доставки или поделитесь своим местоположением с помощью кнопки ниже.'
        )

        return 'TAKE_ADDRESS'
    elif not user_input.isdigit():
        context.bot.send_message(
            chat_id=chat_id,
            text='Неверный формат номера\n'
                 'Повторите пожалуйста ваш номер телефона'
        )
        return 'TAKE_PHONE_NUMBER'


def address_handler(update: Update, context: CallbackContext):
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
            text='Предоставленная информация сохранена в базе, можете приступать к заказу'
        )
        update.message.reply_text('Собрать новый торт или посмотреть заказы?',
                                  reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'MAIN_MENU'


def main_menu_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text='Вы уже зарегистрированы, вы молодец'
    )
    update.message.reply_text(
        'Собрать новый торт или посмотреть заказы?',
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'MAIN_MENU'


def main_menu(update: Update, context: CallbackContext):
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
                    text = 'Возврат в главное меню',
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


def parameter_1(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Количество уровней'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'

    update.message.reply_text('Форма',
                              reply_markup=ReplyKeyboardMarkup(parametr_2_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_2'


def parameter_2(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Форма'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Количество уровней',
                                  reply_markup=ReplyKeyboardMarkup(parametr_1_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_1'

    update.message.reply_text('Топпинг',
                              reply_markup=ReplyKeyboardMarkup(parametr_3_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_3'


def parameter_3(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Топпинг'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Форма',
                                  reply_markup=ReplyKeyboardMarkup(parametr_2_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_2'

    update.message.reply_text('Ягоды',
                              reply_markup=ReplyKeyboardMarkup(parametr_4_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_4'


def parameter_4(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Топпинг',
                                  reply_markup=ReplyKeyboardMarkup(parametr_3_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_3'

    if user_input != 'Пропустить':
        context.user_data['Ягоды'] = user_input
    update.message.reply_text('Декор',
                              reply_markup=ReplyKeyboardMarkup(parametr_5_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_5'


def parameter_5(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Ягоды',
                                  reply_markup=ReplyKeyboardMarkup(parametr_4_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_4'

    if user_input != 'Пропустить':
        context.user_data['Декор'] = user_input
    update.message.reply_text('Мы можем разместить на торте любую надпись, '
                              '\nнапример: «С днем рождения! Введите надпись.',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_6'


def parameter_6(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Декор',
                                  reply_markup=ReplyKeyboardMarkup(parametr_5_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_5'

    if user_input != 'Пропустить':
        context.user_data['Надпись'] = user_input
    update.message.reply_text('Комментарий к заказу',
                              reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return 'PARAMETR_7'



def parameter_7(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    user_id = update.message.from_user.id

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Мы можем разместить на торте любую надпись, '
                                  '\nнапример: «С днем рождения! Введите надпись.',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_6'

    if user_input != 'Пропустить':
        context.user_data['Комментарий к заказу'] = user_input
    with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
        data = json.load(read_file)[str(user_id)]
        contact = '{} {} {}'.format(data['Имя'], data['Фамилия'], data['Номер телефона'])
        context.user_data['Получатель'] = contact
    update.message.reply_text(
        text=f'Контакты по умолчанию: {contact}\n'
             'Выберите контакты по умолчанию или введите новые в формате: имя фамилия, номер телефона',
        reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return 'PARAMETR_7_1'


def parametr_7_1(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text('Комментарий к заказу',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'PARAMETR_7'

    user_id = update.message.from_user.id
    if user_input != 'Выбрать по умолчанию':
        context.user_data['Получатель'] = user_input

    with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
        data = json.load(read_file)[str(user_id)]
        address = data['Адрес']
        context.user_data['Адрес'] = address
    update.message.reply_text(f'Адрес по умолчанию: {address}\n'
                              'Выберите адрес по умолчанию или введите другой',
                              reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True)
                              )
    return 'PARAMETR_8'


def parameter_8(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    user_id = update.message.from_user.id

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)[str(user_id)]
            contact = '{} {} {}'.format(data['Имя'], data['Фамилия'], data['Номер телефона'])
            context.user_data['Получатель'] = contact
        update.message.reply_text(
            text=f'Контакты по умолчанию: {contact}\n'
                 'Выберите контакты по умолчанию или введите новые в формате: имя фамилия, номер телефона',
            reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'PARAMETR_7_1'

    if user_input != 'Выбрать по умолчанию':
        context.user_data['Адрес'] = user_input
    update.message.reply_text(
        'Введите время доставки в формате "DD.MM.YYYY HH-MM" (например: 24.10.2021 18-30) или нажмите "В ближайшее время". '
        '\n Стоимость будет увеличена на 20% при доставке менее чем за 24 часа',
        reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return 'PARAMETR_9'



def parameter_9(update:Update, context:CallbackContext):
    user_input = update.effective_message.text
    user_id = update.message.from_user.id

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        with open("users_contacts.json", 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)[str(user_id)]
            address = data['Адрес']
            context.user_data['Адрес'] = address
        update.message.reply_text(f'Адрес по умолчанию: {address}\n'
                                  'Выберите адрес по умолчанию или введите другой',
                                  reply_markup=ReplyKeyboardMarkup(ok_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True)
                                  )
        return 'PARAMETR_8'

    if user_input == 'В ближайшее время':
        context.user_data['Время доставки'] = user_input
        context.user_data['Срочно'] = 'Да'
        update.message.reply_text('Введите промокод',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'TO_ORDER'

    try:
        time_of_delivery = datetime.strptime(user_input, "%d.%m.%Y %H-%M")
        context.user_data['Время доставки'] = str(time_of_delivery)

        if time_of_delivery < datetime.now() + timedelta(hours=24):
            context.user_data['Срочно'] = 'Да'
        if time_of_delivery < datetime.now():
            update.message.reply_text(
                'Невозможно установить на прошедшее время. Введите заново или нажмите "В ближайшее время".',
                reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return 'PARAMETR_9'
        update.message.reply_text('Введите промокод',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'TO_ORDER'
    except ValueError:
        update.message.reply_text(
            'Некорректное время. Введите время доставки в формате "DD.MM.YYYY HH-MM" '
            '(например: 24.10.2021 18-30) или нажмите "В ближайшее время".',
            reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return 'PARAMETR_9'


def to_order(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'
    if user_input == 'НАЗАД':
        update.message.reply_text(
            'Введите время доставки в формате "DD.MM.YYYY HH-MM" (например: 24.10.2021 18-30) или нажмите "В ближайшее время". '
            '\n Стоимость будет увеличена на 20% при доставке менее чем за 24 часа',
            reply_markup=ReplyKeyboardMarkup(date_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'PARAMETR_9'

    if user_input != 'Пропустить' and user_input not in promocodes:
        update.message.reply_text('Неверный промокод. Повторите ввод или пропустите шаг',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'TO_ORDER'
    order.update(
        {
            'Количество уровней': context.user_data.get('Количество уровней'),
            'Форма': context.user_data.get('Форма'),
            'Топпинг': context.user_data.get('Топпинг'),
            'Ягоды': context.user_data.get('Ягоды'),
            'Декор': context.user_data.get('Декор'),
            'Надпись': context.user_data.get('Надпись'),
            'Получатель': context.user_data.get('Получатель'),
            'Адрес': context.user_data.get('Адрес'),
            'Время доставки': context.user_data.get('Время доставки'),
            'Комментарий к заказу': context.user_data.get('Комментарий к заказу'),
            'Срочно': context.user_data.get('Срочно'),
            'Промокод': user_input
        }
    )
    total_price = 0
    for i in order.values():
        try:
            total_price += price.get(i)
        except:
            pass

    if 'Надпись' in order:
        total_price += 500
    if order['Срочно'] == 'Да':
        total_price = int(total_price * 1.2)
    if order['Промокод'] in promocodes:
        total_price = int(total_price * 0.8)

    order.update({'Стоимость': total_price})

    context.user_data['order'] = order

    update.message.reply_text(f'Стоимость торта составит {total_price} руб. Заказать торт?',
                              reply_markup=ReplyKeyboardMarkup(to_order_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))

    return 'CHECK_TO_ORDER'


def check_to_order(update: Update, context: CallbackContext):
    order = context.user_data.get('order')
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
        json_orders.update(latest_orders)
        orders.append(order)
        json_orders.update({user_id: orders})

    if user_message == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'MAIN_MENU'

    if user_message == 'НАЗАД':
        update.message.reply_text('Введите промокод',
                                  reply_markup=ReplyKeyboardMarkup(pass_keyboard, resize_keyboard=True,
                                                                   one_time_keyboard=True))
        return 'TO_ORDER'

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


def handle_user_reply(update: Update, context: CallbackContext):
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
        'START': start,
        'CHECK_PD_AGREEMENT': pd_agreement_handler,
        'TAKE_PHONE_NUMBER': phone_number_handler,
        'TAKE_ADDRESS': address_handler,
        'MAIN_MENU_HANDLER': main_menu_handler,
        'MAIN_MENU': main_menu,
        'PARAMETR_1': parameter_1,
        'PARAMETR_2': parameter_2,
        'PARAMETR_3': parameter_3,
        'PARAMETR_4': parameter_4,
        'PARAMETR_5': parameter_5,
        'PARAMETR_6': parameter_6,
        'PARAMETR_7': parameter_7,
        'PARAMETR_7_1': parametr_7_1,
        'PARAMETR_8': parameter_8,
        'PARAMETR_9': parameter_9,
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