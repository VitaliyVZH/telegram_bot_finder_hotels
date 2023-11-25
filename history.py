import json
import main

from user import User
from telebot import TeleBot
from translator import translate
from telebot.types import Message


def load_history(id_user: int) -> None:
    """
    Функция создаёт или изменяет history.json. В файле хранится история запросов пользователя.
    :param id_user: (int) id номер пользователя.
    :return: None
    """
    new_data = {
                'the_date': User.user_data[id_user]['date_and_time_command'],
                'command': User.user_data[id_user]['user_command'],
                'list_name_hotels': [User.user_data[id_user]["data_hotels"][hotel]["name hotel"]
                                     for hotel in User.user_data[id_user]["data_hotels"]]
    }

    try:
        main.logger.info('Записываем историю запросов')
        with open(file='history.json', mode='r+') as file:
            data = json.load(file)
            data[str(id_user)].append(new_data)
            file.seek(0)
            json.dump(data, file, indent=4)

    except json.decoder.JSONDecodeError:
        main.logger.info('Перезаписываем историю запросов')
        with open(file='history.json', mode='w') as file:
            data = {id_user: [new_data]}
            json.dump(data, file, indent=4)


def unload_history(bot: TeleBot, message: Message) -> None:
    """
    Функция выводит пользователю историю запросов.
    :param bot: (TeleBot) Экземпляр класса TeleBot.
    :param message: (Message) Тип класса TeleBot
    :return: None
    """
    try:
        main.logger.info('Выгружаем историю запросов')
        with open(file='history.json', mode='r') as file:
            data = json.load(file)

        for num_entry in range(len(data[str(bot.user.id)])):
            found_hotels = ''
            for num_hotels in range(len(data[str(bot.user.id)][num_entry]["list_name_hotels"])):
                found_hotels += f'  {num_hotels + 1}. {data[str(bot.user.id)][num_entry]["list_name_hotels"][num_hotels]}\n'
            bot.send_message(
                chat_id=message.from_user.id,
                text=f'{translate("Дата и время запроса", bot.user.id)}: '
                     f'{data[str(bot.user.id)][num_entry]["the_date"]}\n'
                     f'{translate("Выбранная команда", bot.user.id)}: {data[str(bot.user.id)][num_entry]["command"]}\n'
                     f'{translate("Найденные отели", bot.user.id)}:\n'
                     f'{found_hotels}\n')
        bot.send_message(
            chat_id=message.from_user.id,
            text=f'{translate("Это все результаты из истории запросов", bot.user.id)}')
        main.logger.info('История запросов выдана')

    except json.decoder.JSONDecodeError:
        main.logger.info('История запросов пуста')
        bot.send_message(
            chat_id=message.from_user.id,
            text=f'{translate("История запросов пуста", bot.user.id)}'
              )
