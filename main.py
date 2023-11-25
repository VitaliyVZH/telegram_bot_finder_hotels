import os
import time
import buttons
import history
import text_help
import translator
import response_API
import response_to_user
import logging

from user import User
from telebot import TeleBot
from datetime import datetime
from telebot.types import Message, CallbackQuery
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.environ.get('TOKEN', 'Ключ не найдет')
bot = TeleBot(TOKEN)


logging.basicConfig(
    format=f'\033[38;5;248m %(asctime)s | %(levelname)s | %(filename)s - %(funcName)s | (args:) %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='w',
    encoding='utf-8',
    level=logging.INFO
)


logger = logging.getLogger(__name__)


def data_cleaning(text: str) -> None:
    """
    Функция обнуляет данные, которые ранее вводил пользователь и задаёт новые при условии.
    :param text: (str) Название команды, которую выбрал пользователь.
    :return: None
    """
    if text.startswith('/lowprice') or text.startswith('/highprice'):
        User.user_data[bot.user.id]['price_min'] = 1
        User.user_data[bot.user.id]['price_max'] = 1000000
    User.user_data[bot.user.id]['flag_start_search_city'] = False
    User.user_data[bot.user.id]['data_hotels'].clear()
    User.user_data[bot.user.id]['dict_cities'].clear()
    User.user_data[bot.user.id]['arrival_date'] = ''
    User.user_data[bot.user.id]['date_departure'] = ''
    User.user_data[bot.user.id]['city'] = ''


def main() -> None:
    """
    Родительская функция проекта.
    :return: None
    """
    @bot.message_handler(commands=['help'])
    def help_user(message: Message) -> None:
        """
        Функция отлавливает команду 'help' и используя функцию text_help.help_commands() выводит пользователю список
        возможных команд для телеграмм-бота.
        :param message: (Message или telebot.types.Message) Объект телеграмм-бота позволяющий отправлять сообщения.
        :return: None
        """
        logger.info(message.text)
        User.user_data[bot.user.id]["flag_start_search_city"] = False
        bot.send_message(chat_id=message.chat.id,
                         text=f'{translator.translate(f"Бот может выполнять следующие команды", bot.user.id)}:'
                         f'\n{text_help.help_commands(bot.user.id)}')

    @bot.message_handler(commands=['history'])
    def history_for_user(message: Message) -> None:
        """
        Функция отлавливает команду 'history' и выводит пользователю историю его запросов.
        :param message: (Message или telebot.types.Message) Объект телеграмм-бота позволяющий отправлять сообщения.
        :return: None
        """
        logger.info(message.text)
        User.user_data[bot.user.id]["flag_start_search_city"] = False
        history.unload_history(bot, message)
        bot.send_message(
            chat_id=message.chat.id,
            text=f'{text_help.help_commands(bot.user.id)}'
        )

    @bot.message_handler(commands=['start', 'change_language'])
    def start(message: Message) -> None:
        """
        Функция отлавливает две команды 'start', 'change_language', после чего при помощи  функции
        'buttons.language_selection' пользователю предложат выбрать язык, на котором будет отображаться вся информация.
        :param message: (Message или telebot.types.Message) Объект телеграмм-бота позволяющий отправлять сообщения.
        :return: None
        """
        logger.info(f"{message.text}")
        if message.text == '/start':
            User(bot.user.id)
        User.user_data[bot.user.id]['chat_id'] = message.chat.id
        buttons.language_selection(message)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('language'))
    def callback_language(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой начало данных начиналось на 'Language'. Удаляются кнопки, через
        которые пользователь выбирал язык. Пользователю отправляется сообщение с пояснением, какой язык был выбран.
        Следующим сообщением пользователю приходит приветственное сообщение с перечнем команд, которые может выполнять
        бот, также, через 'buttons.popup_keyboard()' добавляется всплывающие/постоянные кнопки с командами бота.
        :param call: (telebot.types. CallbackQuery) Объект класса telebot.types. CallbackQuery - объект представляет
        входящий запрос обратного вызова от кнопки обратного вызова на встроенной клавиатуре.
        :return: None
        """
        logger.info(f'Выбран язык {call.data}')
        us_id = call.message.from_user.id
        User.user_data[us_id]['flag_start_search_city'] = False
        User.user_data[us_id]['user_language'] = str(call.data).split()[2]
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'{translator.translate(f"Вы выбрали {str(call.data).split()[1]} язык.", us_id)}\n'
                 f'{translator.translate(f"Подготавливаю текст. Подождите несколько секунд", us_id)}',
            reply_markup=None)

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f'{translator.translate("Привет, я бот по поиску отелей, могу выполнять следующие команды", us_id)}:\n'
            f'{text_help.help_commands(us_id)}',
            reply_markup=buttons.popup_keyboard(call.message))

    @bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
    def some_command(message: Message) -> None:
        """
        Функция отлавливает команды 'lowprice', 'highprice', 'bestdeal', если команда была нажата пользователем, тогда
        некоторые данные обнуляются, некоторые объекты начнут ссылаться на указанные данные, далее вызывается функция
        'choose_num_hotels()', которая 'спрашивает' у пользователя, какое количество отелей ему показать.
        :param message: (Message или telebot.types. Message) Объект телеграмм-бота позволяющий отправлять сообщения.
        :return: None
        """
        logger.info(f'Выбрана команда {message.text}')
        data_cleaning(message.text)
        User.user_data[bot.user.id]['user_command'] = message.text.split(' ')[0]
        User.user_data[bot.user.id]['date_and_time_command'] = str(datetime.fromtimestamp(message.date))
        buttons.choose_num_hotels(message)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('number_hotels'))
    def count_hotels(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой начало данных начиналось на 'Number_hotels'. Функция удаляет
        кнопки с выбором кол-ва отелей, отправляет пользователю сообщение с повторением его выбора, далее спрашивает у
        пользователя, в каком городе он ищет отель.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f'Выбрано кол-во отелей: {call.data}')
        us_id = call.message.from_user.id
        text = 'Вам будет показано отелей'
        User.user_data[us_id]['count_hotels'] = int(str(call.data).split()[1])
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'{translator.translate(f"{text}: {int(str(call.data).split()[1])} шт.",us_id)}\n',
                              reply_markup=None)
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f'{translator.translate("В каком городе ищем отель?", us_id)}')
        User.user_data[us_id]['flag_start_search_city'] = True

    @bot.message_handler(content_types=['text'])
    def search_city(message: Message) -> None:
        """
        Функция отлавливает текст введённый пользователем в текстовую строку телеграм бота.
        :param message: (Message или telebot.types.Message) Объект телеграмм-бота позволяющий отправлять сообщения.
        :return: None
        """
        logger.info(f'Указано название города: {message.text}')
        us_id = bot.user.id
        if User.user_data[us_id]['flag_start_search_city'] is True:
            if response_API.city_id(message.text, us_id):
                logger.info(f'Выбран город: {message.text}')
                User.user_data[us_id]['city'] = message.text
                User.user_data[us_id]['flag_start_search_city'] = False
                buttons.buttons_city_filter(message)

            else:
                logger.warning(f'\033[38;5;1mГород не найден: {message.text}')
                bot.send_message(chat_id=message.chat.id,
                                 text=f'{translator.translate("Ничего не найдено, попробуйте ещё раз", us_id)}')

        else:
            logger.warning(f'\033[38;5;1mНесвоевременный вод данных')
            bot.send_message(
                chat_id=message.chat.id,
                text=f'{translator.translate("Ввод данных не действителен", us_id)}')

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('id_city'))
    def callback_adults(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались c 'id', после удаляет
        кнопки, запрашивает у пользователя минимально допустимую для него стоимость номера и вызывает
        функцию get_price_min.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f"Район найден, id: {call.data}")
        us_id = call.message.from_user.id
        User.user_data[us_id]['id_city'] = str(call.data).split()[1]
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        if User.user_data[us_id]['user_command'] == '/bestdeal':
            text = "Введите, подходящую для Вас *минимальную* цену номера за сутки от 1$, до"
            logger.info(f"Запрос на ввод мин. цены отеля")
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f'{translator.translate(text, us_id)} '
                     f'1 000 000$, {translator.translate("число должно быть целым, не дробным", us_id)}',
                parse_mode="Markdown")
            bot.register_next_step_handler(message=call.message, callback=get_price_min)
        else:
            buttons.my_calendar(call.message)

    def get_price_min(message: Message) -> None:
        """
        Функция принимает минимальную стоимость отеля введённую пользователем. И просит пользователя ввести максимально
        допустимую стоимость номера и вызывает следующую функцию get_price_max().
        :param message: (Message) Объект телеграм бота, содержащий в себе необходимые данные для отправки сообщений.
        :return: None
        """
        us_id = bot.user.id
        try:
            if -1 < int(message.text) < 1000000:
                text = "Введите, подходящую для Вас *максимальную* цену номера за сутки, от"
                logger.info('Мин-ная цена введена, запрос максимальной цены get_price_max')
                User.user_data[us_id]['price_min'] = int(message.text)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'{translator.translate(text, us_id)} '
                         f'{User.user_data[us_id]["price_min"]}$ {translator.translate("до", us_id)} 1 000 000$, '
                         f'{translator.translate("число должно быть целым, не дробным", us_id)}',
                    parse_mode="Markdown")
                bot.register_next_step_handler(message=message, callback=get_price_max)
            else:
                logger.warning(f'\033[38;5;1mВведённое число меньше 1 или больше 1 000 000')
                text = "Введённое число меньше 1 или больше 1 000 000, введите данные"
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'{translator.translate(text, us_id)}')
                bot.register_next_step_handler(message=message, callback=get_price_min)

        except ValueError:
            if message.text in ('lowprice', 'highprice', 'bestdeal'):
                some_command(message)
            else:
                bot.send_message(chat_id=message.chat.id, text=f'{text_help.text_for_get_price(us_id)}')
                bot.register_next_step_handler(message=message, callback=get_price_min)

    def get_price_max(message: Message) -> None:
        """
        Функция принимает максимальную стоимость отеля введённую пользователем.
        :param message: (Message) Объект телеграм бота, содержащий в себе необходимые данные для отправки сообщений.
        :return: None
        """
        us_id = bot.user.id
        text = "Укажите, на каком расстоянии отель должен находиться от центра города (в милях)"
        try:
            if User.user_data[us_id]['price_min'] <= int(message.text) <= 1000000:
                User.user_data[us_id]['price_max'] = int(message.text)
                bot.send_message(chat_id=message.chat.id, text=f'{translator.translate(text, us_id)}')
                bot.register_next_step_handler(message=message, callback=get_distance_from_center_city_to_hotel)
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'{translator.translate("Введённое число меньше", us_id)} {User.user_data[us_id]["price_min"]}'
                         f'{translator.translate("или больше 1 000 000, введите данные", us_id)}')
                bot.register_next_step_handler(message=message, callback=get_price_min)
        except ValueError:
            if message.text in ('lowprice', 'highprice', 'bestdeal'):
                some_command(message)
            else:
                bot.send_message(chat_id=message.chat.id, text=f'{text_help.text_for_get_price(us_id)}')
                bot.register_next_step_handler(message=message, callback=get_price_min)

    def get_distance_from_center_city_to_hotel(message: Message) -> None:
        """
        Функция принимает диапазон расстояния, на котором находится отель от центра города.
        :param message: (Message) Объект телеграм бота, содержащий в себе необходимые данные для отправки сообщений.
        :return: None
        """

        us_id = bot.user.id
        try:
            if int(message.text) >= 0:
                logger.info(f'Утверждено расстояние отеля до центра города {message.text}')
                buttons.my_calendar(message)
            else:
                logger.info(f'Расстояние отеля до центра города некорректное {message.text}')
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'{translator.translate("Вы ввели отрицательное число, введите положительное число", us_id)}')
                bot.register_next_step_handler(message=message, callback=get_distance_from_center_city_to_hotel)
        except ValueError:
            if message.text in ('lowprice', 'highprice', 'bestdeal'):
                some_command(message)
            else:
                bot.send_message(chat_id=message.chat.id, text=f'{text_help.text_for_get_price(us_id)}')
                bot.register_next_step_handler(message=message, callback=get_distance_from_center_city_to_hotel)

    @bot.callback_query_handler(func=lambda call: call.data in ('<<', '>>', ' '))
    def callback_worker(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопок с символами '<<', '>>',' '. После того как функция отловила перечисленные
        символы, вызывается календарь 'buttons.my_calendar()', в который передаётся: 1 или -1, в зависимости от символа
        отловленный функцией.
        :param call: (telebot.types.CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f'Переключение месяца {call.data}')
        if call.data == '<<':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.my_calendar(call.message, -1)

        elif call.data == '>>':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.my_calendar(call.message, 1)

        elif call.data == ' ' or call.data is False:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.my_calendar(call.message)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('calendar'))
    def callback_data(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки с форматом даты, после проверяет, может ли этот формат являться датой, после
        проверяет наличие данных в поле даты заезда (User.arrival_date), если дата заезда заполнена, тогда полученная
        дата занесётся в дату выезда (User.date_departure), после чего удалятся кнопки календаря и пользователю
        выведется сообщение.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        us_id = call.message.from_user.id
        try:

            if not User.user_data[us_id]['arrival_date']:
                logger.info(f'Дата заезда в отель {call.data}')
                User.user_data[us_id]['arrival_date'] = str(call.data).split()[1]
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                User.user_data[us_id]['us_shift_month'] = 0
                buttons.my_calendar(call.message)

            else:
                logger.info(f'Дата выезда из отеля {call.data}')
                User.user_data[us_id]['date_departure'] = str(call.data).split()[1]
                User.user_data[us_id]['us_shift_month'] = 0
                User.user_data[us_id]['number_days_in_hotel'] = \
                    int(str((datetime.fromisoformat(User.user_data[us_id]['arrival_date']) -
                             datetime.fromisoformat(User.user_data[us_id]['date_departure'])).days).strip("-")) + 1
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f'{translator.translate("Дата заезда в отель", us_id)}: '
                         f'{User.user_data[us_id]["arrival_date"]}\n'
                         f'{translator.translate("Дата выезда из отеля", us_id)}: '
                         f'{User.user_data[us_id]["date_departure"]}\n'
                         f'{translator.translate("Количество дней пребывания в отеле", us_id)}: '
                         f'{User.user_data[us_id]["number_days_in_hotel"]}',
                    reply_markup=None)
                buttons.number_adults(call.message)

        except (ValueError, AttributeError, IndexError):
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f'{translator.translate("Дата не выбрана, попробуйте ещё раз", us_id)}')
            buttons.my_calendar(call.message)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('adults'))
    def callback_adults(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались на 'adults', после удаляет кнопки,
        отправляет сообщение пользователю информацию о его выборе, выбор пользователя (кол-во взрослых) сохраняется в
        User.num_adults, после вызывается клавиатура для выбора, будут ли проживать дети в номере или нет.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f'Утверждено кол-во взрослых {call.data}')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        User.user_data[call.message.from_user.id]['num_adults'] = int(str(call.data).split()[1])
        buttons.having_children(call.message)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('having_children'))
    def callback_adults(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались на 'having_children', после удаляет
        кнопки, отправляет сообщение пользователю информацию о его выборе. Если пользователь указал, что дети будут
        проживать, в отеле, тогда вызовется функция buttons.number_children(), для выбора кол-ва детей, если
        пользователь указал, что дети в номере проживать не будут, в этом случае вызывается функция
        buttons.availability_photos(), которая выведет кнопки с вопросом, показывать пользователю фотографии или нет.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f'Сделан выбор наличия детей {call.data}')
        if str(call.data).split()[1] == 'Yes':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.number_children(call.message)

        elif str(call.data).split()[1] == 'No':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.availability_photos(call)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('amount_children'))
    def callback_adults(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались на 'amount_children', после удаляет
        кнопки, отправляет сообщение пользователю информацию о его выборе, выбор пользователя сохраняет в объекте
        User.num_children и вызывает функцию buttons.availability_photos(), которая выведет кнопки с вопросом,
        показывать пользователю фотографии или нет.
        :param call: (telebot.types. CallbackQuery) Объект telebot.types позволяет отлавливать нажатия кнопок.
        :return: None
        """
        logger.info(f'Сделан выбор кол-ва детей {call.data}')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        User.user_data[call.message.from_user.id]['num_children'] =\
            ' '.join([str(10) for _ in range(int(call.data[16]))]).replace(' ', ',')
        buttons.availability_photos(call)

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('availability_photos'))
    def photo(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались на 'Availability_photos'.
        :param call: (callbackQuery) Метод telebot.types, позволяет отлавливать донные с нажатых кнопок.
        :return: None
        """
        logger.info(f'Отловлен выбор наличия фото {call.data}')
        us_id = bot.user.id
        if str(call.data).split()[1] == 'Yes':
            User.user_data[us_id]['photo'] = True
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            buttons.choose_num_photos(call)

        elif str(call.data).split()[1] == 'No':
            User.user_data[us_id]['photo'] = False
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=f'{translator.translate(f"Фото отелей отображаться не будут", us_id)}',
                                  reply_markup=None)

            if response_API.hotel_id(bot, call.message):
                response_to_user.answer(call, bot)
            else:
                bot.send_message(chat_id=call.message.chat.id, text=f"{text_help.help_commands(us_id)}")

    @bot.callback_query_handler(func=lambda call: str(call.data).startswith('count_photo'))
    def photo(call: CallbackQuery) -> None:
        """
        Функция отлавливает нажатие кнопки, в которой отправленные данные начинались на 'count_photo'.
        :param call: (telebot.types. CallbackQuery) Объект класса telebot.types. CallbackQuery - объект представляет
        входящий запрос обратного вызова от кнопки обратного вызова на встроенной клавиатуре.
        :return: None
        """
        logger.info(f'Отловлен выбор кол-ва фото {call.data}')
        User.user_data[call.message.from_user.id]['count_photo'] = int(str(call.data).split()[1])
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        if response_API.hotel_id(bot, call.message):
            response_to_user.answer(call, bot)
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f'{translator.translate("Что-то пошло не так, попробуйте ещё раз", bot.user.id)}.\n'
                     f'{text_help.help_commands(call.message.from_user.id)}')

    try:
        bot.polling(none_stop=True, long_polling_timeout=30)
    except Exception as ex:
        logger.warning(f'\033[38;5;1m Ошибка: {ex}')
        time.sleep(5)
        main()


if __name__ == '__main__':
    main()
