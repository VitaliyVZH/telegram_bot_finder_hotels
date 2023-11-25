from collections import OrderedDict


class User:
    """
    Базовый класс содержащий в себе базу данных пользователей.
    Attributes:
        user_data: (dict) база данных пользователей.
    """
    user_data = {}

    @classmethod
    def __init__(cls, id_user: int) -> None:
        """
        Функция добавляет в словарь класса User новый словарь, id номер пользователя - ключ нового словаря.
        :param id_user: (int) id номер пользователя.
        """
        cls.user_data = {id_user: {
            'user_language': 'ru',
            'user_command': '',
            'date_and_time_command': '',
            'name_hotels_found': [],
            'num_hotels': '',
            'city': '',
            'id_city': '',
            'arrival_date': '',
            'date_departure': '',
            'number_days_in_hotel': '',
            'num_adults': '',
            'num_children': None,
            'photo': False,
            'count_photo': 0,
            'popup_keyboard': False,
            'us_shift_month': 0,
            'us_shift_year': 0,
            'dict_cities': {},
            'price_min': 0,
            'price_max': 0,
            'flag_start_search_city': False,
            'data_hotels': OrderedDict()
        }}
