from datetime import date
from typing import Union
from datetime import datetime
from user import User
import main


def if_date(calendar_year: int, calendar_month: int, calendar_day: Union[str, int],
            flag: bool = False) -> Union[datetime.date, bool]:
    """
    Функция проверяет входящие данные на возможность преобразования их в дату.
    Функция принимает год, месяц и число, пробует преобразовать их в дату, если не получается, срабатывает except
    и возвращается False, если получается, проверяет, присвоено ли значение (дата) классу User.arrival_date,
    если да, то переменная new_date начинает ссылаться на User.arrival_date, если User.arrival_date не ссылается на
    данные, тогда переменная new_date ссылается на текущую дату (datetime.now()). Переменная start_date ссылается на
    дату из календаря.
    Переменные datetime.now() и new_date сравниваются, по итогам сравнения, если flag == False, функция возвращает
    полученную дату в формате ГГГГ-мм-дд или False, если flag == True (при проверке даты календаря) - вернётся дата в
    формате ГГГГ-мм-дд или "пробел".
    :param calendar_year: (int) Принимает дату (год) в формате "ГГГГ".
    :param calendar_month: (int) Принимает дату (месяц) в формате "мм".
    :param calendar_day: (Union[str, int]) Принимает дату (день) в формате "дд".
    :param flag: (bool) Принимает True в случае проверки даты календаря.
    :return: (Union[datetime.date (str), bool]) Функция возвращает либо дату в формате "ГГГГ-мм-дд", либо False.
    """
    us_id = main.bot.user.id
    try:
        start_month_date = date(calendar_year, calendar_month, int(calendar_day)).strftime('%Y-%m-%d')
        new_date = datetime.now().strftime('%Y-%m-%d')

        if User.user_data[us_id]['arrival_date']:
            new_date = date(int(User.user_data[us_id]['arrival_date'].split('-')[0]),
                            int(User.user_data[us_id]['arrival_date'].split('-')[1]),
                            int(User.user_data[us_id]['arrival_date'].split('-')[2]) + 1).strftime('%Y-%m-%d')
        if new_date <= start_month_date:
            return date(calendar_year, calendar_month, int(calendar_day))
    except ValueError:
        if flag is True:
            return ' '
        return False
