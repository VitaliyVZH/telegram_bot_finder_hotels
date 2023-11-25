from googletrans import Translator
from user import User


def translate(user_text: str, id_user) -> str:
    """
    Функция переводит слова на указанный язык.
    :param id_user:
    :param user_text: (str) На вход подаётся текст.
    :return: (str) Возвращается переведённый текст.
    """

    translator = Translator()
    result = translator.translate(text=user_text, dest=User.user_data[id_user]['user_language'])
    return result.text
