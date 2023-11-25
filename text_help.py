import main
from translator import translate


def help_commands(us_id: int) -> str:
    """
    Функция возвращает список команд для бота.
    :return: (str) Список команд для бота.
    """
    text = "вывод отелей, наиболее подходящих по цене и расположению от центра"
    main.logger.info('Показываем меню')
    commands = f'\n● /help — {translate("помощь по командам бота", us_id)};\n' \
               f'● /lowprice — {translate("вывод самых дешёвых отелей в городе", us_id)};\n' \
               f'● /highprice — {translate("вывод самых дорогих отелей в городе", us_id)};\n' \
               f'● /bestdeal — {translate(text, us_id)};\n' \
               f'● /history — {translate("вывод истории поиска отелей", us_id)};\n' \
               f'● /change_language — {translate("изменить язык", us_id)}.'
    return commands


def text_for_get_price(us_id: int) -> str:
    """
    Функция отправляет текст.
    :return: (str) Текст для пользователя.
    """
    main.logger.info('Показываем текстовое предупреждение')
    text = f'{translate("Введённое сообщение не соответствует требованиям:", us_id)}\n' \
           f'{translate(" - введённые Вами данные должны быть числом;", us_id)}\n' \
           f'{translate(" - введённое число должно быть целым, не дробным.", us_id)}\n' \
           f'{translate("Повторите ввод в соответствии с требованиями.", us_id)}'
    return text
