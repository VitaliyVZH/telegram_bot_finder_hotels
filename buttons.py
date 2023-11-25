import main
import locale
import calendar
import translator

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, Message, \
    ReplyKeyboardRemove, CallbackQuery

from user import User
from date_check import if_date
from translator import translate
from datetime import datetime, date


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def language_selection(message: Message) -> InlineKeyboardMarkup():
    """
    Функция реализует кнопки для выбора языка.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки language')
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='Русский', callback_data=f'language Русский ru'),
                 InlineKeyboardButton(text='English', callback_data=f'language English  en'))
    main.bot.send_message(message.chat.id, 'Выберете язык\nChoose language', reply_markup=keyboard)


def popup_keyboard(message: Message) -> InlineKeyboardMarkup():
    """
    Функция реализует всплывающие/постоянные кнопки, позволяющие оперативно обращаться к любой опции меню бота.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Всплывающие кнопки')
    us_id = message.from_user.id

    if User.user_data[us_id]['popup_keyboard']:
        main.bot.send_message(message.chat.id, f'{translate("Меняем язык", us_id)}', reply_markup=ReplyKeyboardRemove())
    button_1 = KeyboardButton(text=f'/help - {translate("помощь по командам бота", us_id)}.')
    button_2 = KeyboardButton(text=f'/lowprice - {translate("вывод самых дешёвых отелей в городе", us_id)}.')
    button_3 = KeyboardButton(text=f'/highprice - {translate("вывод самых дорогих отелей в городе", us_id)}.')
    button_4 = KeyboardButton(
        text=f'/bestdeal - {translate("вывод отелей, наиболее подходящих по цене и расположению от центра", us_id)}.')
    button_5 = KeyboardButton(text=f'/history -  {translate("вывод истории поиска отелей", us_id)}.')
    button_6 = KeyboardButton(text=f'/change_language — {translate("изменить язык", us_id)}.')

    help_keyboard_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    User.user_data[us_id]['popup_keyboard'] = True
    return help_keyboard_button.add(button_1).add(button_2).add(button_3).add(button_4).add(button_5).add(button_6)


def choose_num_hotels(message: Message) -> InlineKeyboardMarkup():
    """
    Функция реализует клавиатуру для выбора кол-ва отелей.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора кол-ва отелей')

    button_list = [InlineKeyboardButton(text=f"{i}", callback_data=f"number_hotels {i}") for i in range(1, 11)]
    markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=5))

    main.bot.send_message(
        chat_id=message.chat.id,
        text=f'{translator.translate("Сколько отелей показать?", main.bot.user.id)}',
        reply_markup=markup)


def my_calendar(message: Message, shift: int = 0) -> InlineKeyboardMarkup():
    """
    Функция реализует календарь в телеграм-боте.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :param shift: (int) Переменная может получать следующие значения: 0, 1, -1 в зависимости от переключения
    календаря вперёд или назад.
    :return: (InlineKeyboardMarkup()) Функция возвращает пользователю массив кнопок (календарь).
    """
    main.logger.info(f"Кнопки календаря")
    us_id = main.bot.user.id

    if not User.user_data[us_id]['arrival_date']:
        year = int(datetime.now().strftime('%Y'))   # Текущий год, формат "ГГГГ".
        month = int(datetime.now().strftime('%m'))  # Текущий месяц, формат "мм".
        day = int(datetime.now().strftime('%d'))    # Текущий день, формат "дд".
    else:
        year = int(User.user_data[us_id]['arrival_date'].split('-')[0])
        month = int(User.user_data[us_id]['arrival_date'].split('-')[1])
        day = int(User.user_data[us_id]['arrival_date'].split('-')[2])

    User.user_data[us_id]['us_shift_month'] += shift

    User.us_shift_year = ((month - 1) + User.user_data[us_id]['us_shift_month']) // 12
    edit_month = (month + User.user_data[us_id]['us_shift_month']) % 12
    if edit_month == 0:
        edit_month = 12

    num_days = [num_day
                if if_date(year + User.us_shift_year, edit_month, int(num_day))
                else ' '
                for list_week in calendar.monthcalendar(year, edit_month)
                for num_day in list_week]

    keyboard = InlineKeyboardMarkup()

    days_week = list(calendar.day_abbr)

    if User.user_data[us_id]['user_language'] == 'ru':
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        days_week = list(calendar.day_abbr)

    keyboard.row(InlineKeyboardButton(
        text=translator.translate(date(year + User.us_shift_year, edit_month, day).strftime('%Y %b'), us_id),
        callback_data=' '))

    button_list = [InlineKeyboardButton(text=f"{days_week[num]}", callback_data=f" ") for num in range(7)]
    keyboard = InlineKeyboardMarkup(build_menu(button_list, n_cols=7))

    keyboard.row(
        InlineKeyboardButton(
            text=num_days[0],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[0], True)}'),
        InlineKeyboardButton(
            text=num_days[1],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[1], True)}'),
        InlineKeyboardButton(
            text=num_days[2],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[2], True)}'),
        InlineKeyboardButton(
            text=num_days[3],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[3], True)}'),
        InlineKeyboardButton(
            text=num_days[4],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[4], True)}'),
        InlineKeyboardButton(
            text=num_days[5],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[5], True)}'),
        InlineKeyboardButton(
            text=num_days[6],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[6], True)}'))

    keyboard.row(
        InlineKeyboardButton(
            text=num_days[7],
            callback_data=f'{if_date(year + User.us_shift_year, edit_month, num_days[7], True)}'),
        InlineKeyboardButton(
            text=num_days[8],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[8], True)}'),
        InlineKeyboardButton(
            text=num_days[9],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[9], True)}'),
        InlineKeyboardButton(
            text=num_days[10],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[10], True)}'),
        InlineKeyboardButton(
            text=num_days[11],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[11], True)}'),
        InlineKeyboardButton(
            text=num_days[12],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[12], True)}'),
        InlineKeyboardButton(
            text=num_days[13],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[13], True)}'))

    keyboard.row(
        InlineKeyboardButton(
            text=num_days[14],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[14], True)}'),
        InlineKeyboardButton(
            text=num_days[15],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[15], True)}'),
        InlineKeyboardButton(
            text=num_days[16],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[16], True)}'),
        InlineKeyboardButton(
            text=num_days[17],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[17], True)}'),
        InlineKeyboardButton(
            text=num_days[18],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[18], True)}'),
        InlineKeyboardButton(
            text=num_days[19],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[19], True)}'),
        InlineKeyboardButton(
            text=num_days[20],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[20], True)}'))

    keyboard.row(
        InlineKeyboardButton(
            text=num_days[21],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[21], True)}'),
        InlineKeyboardButton(
            text=num_days[22],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[22], True)}'),
        InlineKeyboardButton(
            text=num_days[23],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[23], True)}'),
        InlineKeyboardButton(
            text=num_days[24],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[24], True)}'),
        InlineKeyboardButton(
            text=num_days[25],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[25], True)}'),
        InlineKeyboardButton(
            text=num_days[26],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[26], True)}'),
        InlineKeyboardButton(
            text=num_days[27],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[27], True)}'))

    keyboard.row(
        InlineKeyboardButton(
            text=num_days[28],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[28], True)}'),
        InlineKeyboardButton(
            text=num_days[29],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[29], True)}'),
        InlineKeyboardButton(
            text=num_days[30],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[30], True)}'),
        InlineKeyboardButton(
            text=num_days[31],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[31], True)}'),
        InlineKeyboardButton(
            text=num_days[32],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[32], True)}'),
        InlineKeyboardButton(
            text=num_days[33],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[33], True)}'),
        InlineKeyboardButton(
            text=num_days[34],
            callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[34], True)}'))

    if len(num_days) > 35:
        keyboard.row(
            InlineKeyboardButton(
                text=num_days[35],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[35], True)}'),
            InlineKeyboardButton(
                text=num_days[36],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[36], True)}'),
            InlineKeyboardButton(
                text=num_days[37],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[37], True)}'),
            InlineKeyboardButton(
                text=num_days[38],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[38], True)}'),
            InlineKeyboardButton(
                text=num_days[39],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[39], True)}'),
            InlineKeyboardButton(
                text=num_days[40],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[40], True)}'),
            InlineKeyboardButton(
                text=num_days[41],
                callback_data=f'calendar {if_date(year + User.us_shift_year, edit_month, num_days[41], True)}'))

    if month < (month + User.user_data[us_id]['us_shift_month']):
        keyboard.add(InlineKeyboardButton(text='<<', callback_data='<<'),
                     InlineKeyboardButton(
                         text=translate(date(year + User.us_shift_year, edit_month, day).strftime('%Y %b'), us_id),
                         callback_data=' '),
                     InlineKeyboardButton(text='>>', callback_data='>>'))
    else:
        keyboard.add(InlineKeyboardButton(text=' ', callback_data=' '),
                     InlineKeyboardButton(
                         text=translate(date(year + User.us_shift_year, edit_month, day).strftime('%Y %b'), us_id),
                         callback_data=' '),
                     InlineKeyboardButton(text='>>', callback_data='>>'))

    text = ''
    if not User.user_data[us_id]['arrival_date']:
        text = f'{translator.translate("Укажите дату заезда в отель", us_id)}'
    elif User.user_data[us_id]['arrival_date'] and not User.user_data[us_id]['date_departure']:
        text = f'{translator.translate("Укажите дату отбытия", us_id)}'
    main.bot.send_message(chat_id=message.chat.id, text=f'{translate(text, us_id)}', reply_markup=keyboard)


def number_adults(message: Message) -> InlineKeyboardMarkup():
    """
    Реализация кнопок для выбора количества взрослых, которые будут проживать в отеле.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора кол-ва взрослых')
    text = "Сколько взрослых будет проживать в номере (от 17 лет)?"
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='1', callback_data=f'adults 1'),
                 InlineKeyboardButton(text='2', callback_data=f'adults 2'),
                 InlineKeyboardButton(text='3', callback_data=f'adults 3'),
                 InlineKeyboardButton(text='4', callback_data=f'adults 4'),
                 InlineKeyboardButton(text='5', callback_data=f'adults 5'))

    keyboard.row(InlineKeyboardButton(text='6', callback_data=f'adults 6'),
                 InlineKeyboardButton(text='7', callback_data=f'adults 7'),
                 InlineKeyboardButton(text='8', callback_data=f'adults 8'),
                 InlineKeyboardButton(text='9', callback_data=f'adults 9'),
                 InlineKeyboardButton(text='10', callback_data=f'adults 10'))

    keyboard.row(InlineKeyboardButton(text='11', callback_data=f'adults 11'),
                 InlineKeyboardButton(text='12', callback_data=f'adults 12'),
                 InlineKeyboardButton(text='13', callback_data=f'adults 13'),
                 InlineKeyboardButton(text='14', callback_data=f'adults 14'),
                 InlineKeyboardButton(text='15', callback_data=f'adults 15'))

    keyboard.row(InlineKeyboardButton(text='16', callback_data=f'adults 16'),
                 InlineKeyboardButton(text='17', callback_data=f'adults 17'),
                 InlineKeyboardButton(text='18', callback_data=f'adults 18'),
                 InlineKeyboardButton(text='19', callback_data=f'adults 19'),
                 InlineKeyboardButton(text='20', callback_data=f'adults 20'))
    main.bot.send_message(message.chat.id,
                          f'{translator.translate(text, main.bot.user.id)}',
                          reply_markup=keyboard)


def having_children(message: Message) -> InlineKeyboardMarkup():
    """
    Реализация кнопок "Да", "Нет" для указания, будут ли дети.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора наличия детей')
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=f'{translator.translate("Да", main.bot.user.id)}',
                                      callback_data=f'having_children Yes'),
                 InlineKeyboardButton(text=f'{translator.translate("Нет", main.bot.user.id)}',
                                      callback_data=f'having_children No'))
    main.bot.send_message(
        chat_id=message.chat.id,
        text=f'{translator.translate("С вами будут дети?", main.bot.user.id)}',
        reply_markup=keyboard
    )


def number_children(message: Message) -> InlineKeyboardMarkup():
    """
    Реализация кнопок для выбора количества детей.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора кол-ва детей')
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='1', callback_data=f'amount_children 1'),
                 InlineKeyboardButton(text='2', callback_data=f'amount_children 2'),
                 InlineKeyboardButton(text='3', callback_data=f'amount_children 3'),
                 InlineKeyboardButton(text='4', callback_data=f'amount_children 4'))

    keyboard.row(InlineKeyboardButton(text='5', callback_data=f'amount_children 5'),
                 InlineKeyboardButton(text='6', callback_data=f'amount_children 6'),
                 InlineKeyboardButton(text='7', callback_data=f'amount_children 7'),
                 InlineKeyboardButton(text='8', callback_data=f'amount_children 8'))

    main.bot.send_message(chat_id=message.chat.id,
                          text=f'{translator.translate("Выберете количество детей (до 18 лет)?", main.bot.user.id)}',
                          reply_markup=keyboard)


def buttons_city_filter(message: Message) -> InlineKeyboardMarkup():
    """
    Функция реализует кнопки с перечислением городов с их округами.
    :param message: (Message) Объект telebot.type, содержит в себе данные о пользователе.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора района поиска отеля')
    keyboard = InlineKeyboardMarkup()
    for key, values in User.user_data[main.bot.user.id]['dict_cities'].items():
        keyboard.add(InlineKeyboardButton(
            text=f'{translate(key, main.bot.user.id)}',
            callback_data=f'id_city {values}'
        ))

    main.bot.send_message(chat_id=message.chat.id, text=f'{translate("Уточните район поиска:", main.bot.user.id)}',
                          reply_markup=keyboard, parse_mode="Markdown")


def availability_photos(call: CallbackQuery) -> InlineKeyboardMarkup():
    """
    Функция реализует две кнопки "Да", "Нет".
    При вызове функции пользователю задаётся вопрос, нужны ли ему фотографии и выводятся кнопки.
    :param call: (CallbackQuery) Входящий параметр "call" позволяет отправлять сообщения.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора наличия фото')
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=f'{translator.translate("Да", main.bot.user.id)}',
                                      callback_data=f'availability_photos Yes'),
                 InlineKeyboardButton(text=f'{translator.translate("Нет", main.bot.user.id)}',
                                      callback_data=f'availability_photos No'))
    main.bot.send_message(
        chat_id=call.message.chat.id, text=f'{translator.translate("Показывать фотографии отеля?", main.bot.user.id)}',
        reply_markup=keyboard, timeout=40)


def choose_num_photos(call: CallbackQuery) -> InlineKeyboardMarkup():
    """
    Функция реализует клавиатуру для выбора кол-ва фотографий.
    При вызове функции пользователю задаётся вопрос, нужны ли ему фотографии и выводятся кнопки.
    :param call: (CallbackQuery) Входящий параметр "call" позволяет отправлять сообщения пользователю.
    :return: (InlineKeyboardMarkup()) Возвращается массив кнопок.
    """
    main.logger.info('Кнопки выбора кол-ва фотографий')
    text = 'Выберете количество фотографий, которое будет отображаться для каждого отеля:'
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='1', callback_data='count_photo 1'),
                 InlineKeyboardButton(text='2', callback_data='count_photo 2'),
                 InlineKeyboardButton(text='3', callback_data='count_photo 3'),
                 InlineKeyboardButton(text='4', callback_data='count_photo 4'),
                 InlineKeyboardButton(text='5', callback_data='count_photo 5'))

    keyboard.row(InlineKeyboardButton(text='6', callback_data='count_photo 6'),
                 InlineKeyboardButton(text='7', callback_data='count_photo 7'),
                 InlineKeyboardButton(text='8', callback_data='count_photo 8'),
                 InlineKeyboardButton(text='9', callback_data='count_photo 9'),
                 InlineKeyboardButton(text='10', callback_data='count_photo 10'))

    main.bot.send_message(
        chat_id=call.message.chat.id,
        text=f'{translator.translate(text, main.bot.user.id)}',
        reply_markup=keyboard)
