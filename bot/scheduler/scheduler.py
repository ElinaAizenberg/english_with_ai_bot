import logging
from aiogram import Bot
from openai import OpenAI
from fluentogram import TranslatorHub

from bot.database.connection_pool import ConnectionPool
from bot.database.database_handler import DatabaseHandler
from bot.keyboards.keyboards import get_new_word_idiom_keyboard
from bot.services.utils import check_user_status
from bot.services.openai import get_new_word_idiom
from bot.lexicon.lexicon import get_topic


logger = logging.getLogger(__name__)


async def send_new_words_idioms(bot: Bot, openai_client: OpenAI, pool: ConnectionPool, translator_hub: TranslatorHub):
    """
    Send new vocabulary every day tailored to user's settings.
    - get all active users and check their end of subscription time;
    - froze those whose subscription is over with notification;
    - create a dictionary for other users with their settings: level + topic;
    - create vocabulary sets for every pair with OpenAi API;
    - for every user reset its checks/daily options, check if new items are not presented in user's storage, create new
    vocabulary set if needed;
    - send messages with vocabulary and keyboard: Next + Cambridge dictionary link.
    """
    connection = pool.acquire()
    db = DatabaseHandler(connection)

    active_users: list[dict[str, str]] = db.get_active_users()

    if not active_users:
        logger.info("---------------No active users--------------------")
        pool.release(connection)
        return

    pairs: dict[str, []] = get_levels_topics_accounts(active_users, db)

    for pair, user_ids in pairs.items():
        level: str = pair.split('_', 1)[0]
        topic_key: str = pair.split('_', 1)[-1]
        topic: str = get_topic(topic_key)

        # inform users whose trial period is over, that their status is 'frozen'.
        if pair == 'None':
            for user_id in user_ids:
                user_language = db.get_user_column_data(user_id, 'language')
                i18n = translator_hub.get_translator_by_locale(locale=user_language)
                await bot.send_message(user_id, i18n.get('trial-over-message'))

        else:
            new_word: dict[str, str] = get_new_word_idiom(openai_client, level, topic, 'word')
            new_idiom: dict[str, str] = get_new_word_idiom(openai_client, level, topic, 'idiom')

            for user_id in user_ids:
                user_items = {'word': dict(new_word),
                              'idiom': dict(new_idiom)
                              }
                db.daily_user_reset(user_id)

                user_language = db.get_user_column_data(user_id, 'language')
                i18n = translator_hub.get_translator_by_locale(locale=user_language)

                keyboard = {'text': i18n.get('next-button')}

                for item_name, item_dict in user_items.items():
                    # check if user has already received this item before, generate new set until the check is False
                    while db.check_word_exists_in_column(user_id, item_name, item_dict.get('value')):
                        user_items = db.get_user_all_items(user_id, item_name)
                        item_dict = get_new_word_idiom(openai_client, level, topic, item_name, user_items)

                    db.register_new_item(user_id, item_name, item_dict.get('value'))

                    new_text = i18n.get('new-word-idiom-message', item=item_name, value=item_dict.get('value'),
                                        meaning=item_dict.get('meaning'),
                                        example=item_dict.get('example'))

                    new_text += '\n\n' + i18n.get('next-option-message')
                    keyboard['callback'] = 'next_' + item_name

                    await bot.send_message(user_id, new_text,
                                           reply_markup=get_new_word_idiom_keyboard(keyboard, item_dict.get('url')))

    pool.release(connection)


def get_levels_topics_accounts(active_users: list[dict[str, str]], database: DatabaseHandler):
    """
    Create a dictionary: key - {level}_{topic}, value - list if active user_ids. If user's status changes today,
    update its status in the database and add user_id in the list under the key 'None'.
    """
    pairs: dict[str, []] = {'None': []}

    for user in active_users:
        user_id = user.get('user_id')
        user_subscription_end = user.get('subscription_end')

        if check_user_status(user_subscription_end):  # checks if end of subscription is later than current time (UTC)
            user_data = database.get_user_data(user_id)
            pair_key = user_data.get('level') + '_' + user_data.get('topic')

            if pair_key in pairs.keys():
                pairs[pair_key].append(user_id)
            else:
                pairs[pair_key] = [user_id]
        else:
            database.change_column_value(user_id, 'users', 'status', '2')
            pairs['None'].append(user_id)

    return pairs
