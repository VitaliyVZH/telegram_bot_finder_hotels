import os
import re
import json
import main
import requests
import telebot

from user import User
from requests import request
from translator import translate
from googletrans import Translator
from telebot.types import Message
from dotenv import load_dotenv
load_dotenv()


KEY = os.environ.get('key', 'Ключ не найдет')


def city_id(user_city: str, us_id: int) -> bool:
    """
    Функция производит GET запрос к API.
    :param us_id: (int) id номер пользователя, позволяет ссылаться на его данные в словаре.
    :param user_city: (str) Название города, которое ввёл пользователь.
    :return: (bool) Возвращает True или False в зависимости от результата request запроса.
    """
    main.logger.info('Делаем GET вызов по id города')
    city = Translator()
    name_city = city.translate(text=user_city, dest='en')

    url = "https://hotels-com-provider.p.rapidapi.com/v1/destinations/search"

    querystring = {"query": name_city.text, "currency": "USD", "locale": "en_US"}

    headers = {
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
        "X-RapidAPI-Key": KEY
    }

    response = request(method="GET", url=url, headers=headers, params=querystring)

    if response.ok:
        main.logger.info('GET запрос по id города - УДАЧНЫЙ')
        data = json.loads(response.text)

        for i_entities in range(len(data['suggestions'][0]['entities'])):
            caption = data['suggestions'][0]['entities'][i_entities]['caption']
            destination_id = data['suggestions'][0]['entities'][i_entities]['destinationId']

            try:
                start = str(caption[:re.search(
                    pattern=r'[(]*<span.+</span>',
                    string=caption).start()]).rstrip().rstrip(',')
                finish = str(caption[re.search(
                    pattern=r'<span.+</span>[C]*[)]*',
                    string=caption).end():]).lstrip(',').lstrip()
                total = f"{start}, {finish}".strip(', ')
                User.user_data[us_id]['dict_cities'][total] = destination_id
            except AttributeError:
                User.user_data[us_id]['dict_cities'][caption] = destination_id

        if User.user_data[us_id]['dict_cities']:
            main.logger.info('Список отелей с их id набран')
            return True
    main.logger.warning(f'\033[38;5;1m GET запрос по id города - Не удался {response.status_code}')
    return False


def hotel_id(bot: telebot.TeleBot, message: Message) -> bool:
    """
    Функция производит API запрос по параметрам пользователя, ответ сохраняется во временном словаре, временный словарь
    сортируется в зависимости от команды выбранной пользователем
    """
    main.logger.info('Делаем GET вызов по id отеля')

    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"

    if User.user_data[bot.user.id]['num_children']:
        querystring = {"checkin_date": User.user_data[bot.user.id]['arrival_date'],
                       "checkout_date": User.user_data[bot.user.id]['date_departure'],
                       "sort_order": "STAR_RATING_HIGHEST_FIRST",
                       "destination_id": User.user_data[bot.user.id]['id_city'],
                       "adults_number": User.user_data[bot.user.id]['num_adults'], "locale": "en_US",
                       "currency": "USD", "children_ages": User.user_data[bot.user.id]['num_children'],
                       "price_min": User.user_data[bot.user.id]['price_min'],
                       "star_rating_ids": "3,4,5", "accommodation_ids": "20,8,15,5,1",
                       "price_max": User.user_data[bot.user.id]['price_max'],
                       "page_number": "1", "theme_ids": "14,27,25", "amenity_ids": "527,2063", "guest_rating_min": "3"}
    else:
        querystring = {"checkin_date": User.user_data[bot.user.id]['arrival_date'],
                       "checkout_date": User.user_data[bot.user.id]['date_departure'],
                       "sort_order": "STAR_RATING_HIGHEST_FIRST",
                       "destination_id": User.user_data[bot.user.id]['id_city'],
                       "adults_number": User.user_data[bot.user.id]['num_adults'], "locale": "en_US",
                       "currency": "USD", "price_min": User.user_data[bot.user.id]['price_min'],
                       "star_rating_ids": "3,4,5", "accommodation_ids": "20,8,15,5,1",
                       "price_max": User.user_data[bot.user.id]['price_max'],
                       "page_number": "1", "theme_ids": "14,27,25", "amenity_ids": "527,2063", "guest_rating_min": "3"}

    headers = {
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
        "X-RapidAPI-Key": KEY
    }

    response = requests.request(method="GET", url=url, headers=headers, params=querystring)

    if response.ok:
        main.logger.info('GET запрос по id ОТЕЛЯ - УДАЧНЫЙ')
        data = json.loads(response.text)

        sort_data_hotels = None

        if str(User.user_data[bot.user.id]['user_command']).startswith('/lowprice'):
            sort_data_hotels = sorted(
                data['searchResults']["results"],
                key=lambda keys: int(str(keys['ratePlan']['price']['current'][1:]).replace(',', '')),
                reverse=False
            )

        elif str(User.user_data[bot.user.id]['user_command']).startswith('/highprice'):
            sort_data_hotels = sorted(
                data['searchResults']["results"],
                key=lambda keys: int(str(keys['ratePlan']['price']['current'][1:]).replace(',', '')),
                reverse=True
            )

        elif str(User.user_data[bot.user.id]['user_command']).startswith('/bestdeal'):
            sort_data_hotels = sorted(data['searchResults']["results"],
                                      key=lambda keys:
                                      (float(''.join(keys["landmarks"][0]['distance']).split(' ')[0]),
                                       int(str(keys['ratePlan']['price']['current'][1:]).replace(',', ''))),
                                      reverse=False)

        iterator_id_hotels = iter(sort_data_hotels)
        try:
            for _ in range(User.user_data[bot.user.id]['count_hotels']):
                info_hotels = next(iterator_id_hotels)

                User.user_data[bot.user.id]['data_hotels'][info_hotels['id']] = {
                    'name hotel': info_hotels['name'],
                    'address hotel': info_hotels['address']['streetAddress'],
                    'location_from_city_center': float(''.join(info_hotels["landmarks"][0]['distance']).split(' ')[0]),
                    'current': int(str(info_hotels['ratePlan']['price']['current'][1:]).replace(',', '')),
                    'coordinate': {'lat': info_hotels['coordinate']['lat'], 'lon': info_hotels['coordinate']['lon']},
                    'photo_hotels': None
                }
        except StopIteration:
            main.logger.info('отелей меньше, чем запрашивал пользователь')
            text = "Отелей найдено меньше, чем Вы запрашивали, найдено отелей"
            bot.send_message(
                chat_id=message.chat.id,
                text=f'{translate(text, bot.user.id)}: '
                     f'{len(User.user_data[bot.user.id]["data_hotels"])}')

        if User.user_data[bot.user.id]['photo']:
            main.logger.info('Делаем GET запрос по id отеля, поиск фото')

            for id_hotels in User.user_data[bot.user.id]['data_hotels']:

                url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/photos"

                querystring = {"hotel_id": id_hotels}

                headers = {
                    "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
                    "X-RapidAPI-Key": KEY
                }

                response = requests.request(method="GET", url=url, headers=headers, params=querystring)

                if response.ok:
                    main.logger.info('Фотографии отеля найдены')
                    data_2 = json.loads(response.text)

                    list_photo_hotels = [photo['mainUrl'] for photo in data_2]
                    User.user_data[bot.user.id]['data_hotels'][id_hotels]['photo_hotels'] = \
                        list_photo_hotels[:User.user_data[bot.user.id]['count_photo']]

                else:
                    main.logger.warning(f'\033[38;5;1m Неуспешный GET запрос по id отеля, поиск фото')
                    return False

        main.logger.info('Успешный GET запрос по поиску фото отеля')
        return True
