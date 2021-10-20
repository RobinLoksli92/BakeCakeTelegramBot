from dotenv import load_dotenv
import os
import telegram
from telegram import Update
from telegram import replymarkup
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
from telegram.files.contact import Contact


states_database = {}   # Стейт пользователя

users_pd = {}          # Словарь с персональной инфой по пользователям

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


def check_pd_agreement(update:Update, context:CallbackContext):
    user_reply = update.effective_message.text
    chat_id = update.effective_message.chat_id

    if user_reply == 'Согласен':
        user_last_name = update.effective_message.chat.last_name
        user_first_name = update.effective_message.chat.first_name
        users_pd['Фамилия'] = user_last_name
        users_pd['Имя'] = user_first_name
        context.bot.send_message(
        chat_id=chat_id,
        text = f'{user_last_name} {user_first_name}, вы соглались на обработку ваших ПД.\n'
               'Теперь введите пожалуйста ваш номер телефона или отправьте контакт',
               reply_markup = ReplyKeyboardMarkup(phone_number_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_PHONE_NUMBER'
        

    elif user_reply == 'Не согласен':
        context.bot.send_message(
        chat_id=chat_id,
        text = 'Вы отказались от обработки ваших ПД'
        )
        return 'START'


def take_phone_number(update:Update, context:CallbackContext):
    user_input = update.effective_message.text    #Здесь то, что ввел пользователь. Должен быть номер телефона
    chat_id = update.effective_message.chat_id

    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        users_pd['Номер телефона'] = user_phone_number  
        context.bot.send_message(                     
        chat_id = chat_id,
        text = 'Теперь, укажите адрес доставки',
        reply_markup=ReplyKeyboardMarkup(address_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'TAKE_ADDRESS'

    elif user_input.isdigit():
        users_pd['Номер телефона'] = user_input        
        context.bot.send_message(                     
            chat_id = chat_id,
            text = 'Теперь, укажите адрес доставки',
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

    
def take_address(update:Update, context:CallbackContext):
    user_input = update.effective_message.text   
    chat_id = update.effective_message.chat_id

    if update.message.location is not None:
        user_location = update.message.location 
        context.bot.send_message(
            chat_id=chat_id,
            text = f'Ваш адрес: {user_location}'
        )
    elif user_input:
        context.bot.send_message(
            chat_id=chat_id,
            text = f'Ваш адрес: {user_input}'
        )


def main_menu_handler(update:Update, context: CallbackContext):
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
        'CHECK_PD_AGREEMENT' : check_pd_agreement,
        'TAKE_PHONE_NUMBER' : take_phone_number,
        'TAKE_ADDRESS' : take_address,

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
    dispatcher.add_handler(MessageHandler(Filters.contact & Filters.location, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()

#test