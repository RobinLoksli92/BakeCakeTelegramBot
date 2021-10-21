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

from telegram.utils.helpers import effective_message_type


states_database = {}   # Стейт пользователя

users_pd = {}          # Словарь с персональной инфой по пользователям

       # Словарь с ключем = id пользователя и значением в виде словаря с персональной инфой

json_dict = {}

pd_agreement_keyboard = [
    [KeyboardButton('Согласен'), KeyboardButton('Не согласен')],
]

phone_number_keyboard = [
    [KeyboardButton('Отправить контакты', request_contact=True)]
]

address_keyboard = [
    [KeyboardButton('Отправить адрес', request_location=True)]
]


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
        json_dict.update(users_dict)
        with open('users_contacts.json', 'w', encoding='utf-8') as file:
            json.dump(json_dict, file, ensure_ascii=False)
        context.bot.send_message(
            chat_id=chat_id,
            text = 'Предоставленная информация сохранена в базе, можете приступать к заказу'
        )

def main_menu_handler(update:Update, context: CallbackContext):
    pass


def handle_user_reply(update:Update, context:CallbackContext):
    
    with open('users_contacts.json', 'r', encoding='utf-8') as file:
        users_json_dict = json.load(file)
        json_dict.update(users_json_dict)

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
            context.bot.send_message(
                chat_id=chat_id,
                text = 'Вы уже зарегистрированы, вы молодец'
            )   
        else:
            user_state = 'START'

    else:
        user_state = states_database.get(chat_id)

    states_functions = {
        'START' : start,
        'CHECK_PD_AGREEMENT' : pd_agreement_handler,
        'TAKE_PHONE_NUMBER' : phone_number_handler,
        'TAKE_ADDRESS' : address_handler,

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
    updater.start_polling()
    # with open('users_contacts.json', 'r', encoding='utf-8') as file:
    #     users_json_dict = json.load(file)
    # print(users_json_dict)
    


if __name__ == '__main__':
    main()

