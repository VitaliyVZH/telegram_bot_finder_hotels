import main
import text_help
import translator

from user import User
from history import load_history
from telebot.types import InputMediaPhoto


def answer(call, bot) -> None:
    text = translator.translate('день', bot.user.id)
    if User.user_data[bot.user.id]['number_days_in_hotel'] in (2, 3, 4):
        text = translator.translate('дня', bot.user.id)
    elif User.user_data[bot.user.id]['number_days_in_hotel'] > 4:
        text = translator.translate('дней', bot.user.id)

    if len(User.user_data[bot.user.id]['data_hotels']) == 0:
        main.logger.info('Отелей не найдено')
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'{translator.translate("По Вашему запросу ничего не найдено", bot.user.id)}')
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'{text_help.help_commands(bot.user.id)}')

    else:
        main.logger.info('Пользователю  выдаётся информация об отелях')
        for id_hotels in User.user_data[bot.user.id]["data_hotels"]:
            name_url = f'www.hotels.com.{User.user_data[bot.user.id]["data_hotels"][id_hotels]["name hotel"]}'
            url = f'https://www.hotels.com/ho{id_hotels}'
            url_text = f'[{name_url}]({url})'

            current = User.user_data[bot.user.id]["data_hotels"][id_hotels]["current"]

            bot.send_message(
                chat_id=call.message.chat.id,
                text=f'{translator.translate("Название отеля", bot.user.id)}: '
                     f'{User.user_data[bot.user.id]["data_hotels"][id_hotels]["name hotel"]}\n'
                     f'{translator.translate("Адрес отеля", bot.user.id)}: '
                     f'{User.user_data[bot.user.id]["data_hotels"][id_hotels]["address hotel"]}\n'
                     f'{translator.translate("Отдалённость отеля от центра города", bot.user.id)}: '
                     f'{User.user_data[bot.user.id]["data_hotels"][id_hotels]["location_from_city_center"]} '
                     f'{translator.translate("миль", bot.user.id)}\n'
                     f'{translator.translate("Стоимость проживания за одни сутки", bot.user.id)}: '
                     f'{User.user_data[bot.user.id]["data_hotels"][id_hotels]["current"]}$\n'
                     f'{translator.translate("Стоимость проживания за", bot.user.id)} '
                     f'{User.user_data[bot.user.id]["number_days_in_hotel"]} {text}: '
                     f'{current * User.user_data[bot.user.id]["number_days_in_hotel"]}$\n'
                     f'{translator.translate("Ссылка на сайт отеля", bot.user.id)}:\n{url_text}\n',
                parse_mode='Markdown'
            )

            if User.user_data[bot.user.id]['photo']:
                main.logger.info('Пользователю  выдаётся информация о фото отелей')
                name_hotel = User.user_data[bot.user.id]["data_hotels"][id_hotels]["name hotel"]

                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f'{translator.translate("Фотографии отеля", bot.user.id)} {name_hotel}:')

                list_url_photo = []
                for url_photo in User.user_data[bot.user.id]["data_hotels"][id_hotels]["photo_hotels"]:
                    list_url_photo.append(InputMediaPhoto(str(url_photo)))
                try:
                    bot.send_media_group(chat_id=call.message.chat.id, media=list_url_photo)

                except Exception as ex:
                    main.logger.info('Фото отелей не получилось вывести', ex)
                    bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f'{translator.translate("Фотографии отеля", bot.user.id)} {name_hotel} '
                             f'{translator.translate("не загрузились", bot.user.id)}')

        load_history(bot.user.id)

        main.logger.info('Все отели и фото показаны')
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"{translator.translate('Вся информация по отелям показана, поиск завершен', bot.user.id)}"
        )

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"{translator.translate(text_help.help_commands(bot.user.id), bot.user.id)}"
        )
