from aiogram import F, Router
from aiogram.types import CallbackQuery
from openai import OpenAI
from fluentogram import TranslatorRunner, TranslatorHub

from bot.database.database_handler import DatabaseHandler
from bot.services.utils import handle_account_command_or_callback
from bot.keyboards.keyboards import (get_settings_keyboard, get_settings_language_keyboard,
                                     get_settings_level_keyboard, get_settings_topic_keyboard,
                                     get_new_word_idiom_keyboard)
from bot.lexicon.lexicon import LEVEL_BUTTONS, TOPIC_BUTTONS, get_topic
from bot.services.openai import get_new_word_idiom


router = Router()


@router.callback_query(F.data.in_(['select_en', 'select_ru']))
async def process_language_selection_button_press(callback: CallbackQuery, db: DatabaseHandler,
                                                  translator_hub: TranslatorHub):
    """Handler for an initial language selection that comes after /start command for a new user."""
    selected_language = 'ru'
    if callback.data == 'select_en':
        selected_language = 'en'

    i18n = translator_hub.get_translator_by_locale(locale=selected_language)
    await callback.message.edit_text(text=i18n.get('language-selected-message'))
    await callback.message.answer(text=i18n.get('short-description-message'))
    await callback.message.answer(text=i18n.get('activate-message'))

    db.change_column_value(callback.from_user.id, 'users', 'language', selected_language)


@router.callback_query(F.data == 'back_to_settings')
async def process_back_button_press(callback: CallbackQuery, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for a 'Back' button in /account keyboards (language, level, topic)."""
    user_data = db.get_user_data(callback.from_user.id)
    message_content = handle_account_command_or_callback(user_data, i18n)

    await callback.message.edit_text(text=message_content.get('text'),
                                     reply_markup=get_settings_keyboard(message_content.get('keyboard')))


@router.callback_query(F.data == 'remove_message')
async def process_close_button_press(callback: CallbackQuery):
    """handler for a 'Close' button in /account keyboard."""
    await callback.message.delete()


@router.callback_query(F.data == 'select_language')
async def process_lang_selection_button_press(callback: CallbackQuery, i18n: TranslatorRunner):
    """Handler for a button 'Select language' in /account keyboard."""
    keyboard = {'back': i18n.get('back-button')}
    await callback.message.edit_text(text=callback.message.text, reply_markup=get_settings_language_keyboard(keyboard))


@router.callback_query(F.data == 'select_level')
async def process_level_selection_button_press(callback: CallbackQuery, i18n: TranslatorRunner):
    """Handler for a button 'Select level' in /account keyboard."""
    keyboard = {'back': i18n.get('back-button')}
    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=get_settings_level_keyboard(keyboard))


@router.callback_query(F.data == 'select_topic')
async def process_topic_selection_button_press(callback: CallbackQuery, i18n: TranslatorRunner):
    """Handler for a button 'Select topic' in /account keyboard."""
    keyboard = {'art': i18n.get('art-topic'),
                'social': i18n.get('social-topic'),
                'tech': i18n.get('tech-topic'),
                'culture': i18n.get('culture-topic'),
                'general': i18n.get('general-topic'),
                'back': i18n.get('back-button')}
    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=get_settings_topic_keyboard(keyboard))


@router.callback_query(F.data.in_(['select_english', 'select_russian']))
async def process_language_button_press(callback: CallbackQuery, i18n: TranslatorRunner,
                                        translator_hub: TranslatorHub, db: DatabaseHandler):
    """Handler for language selection buttons."""
    user_language = db.get_user_column_data(callback.from_user.id, 'language')

    if callback.data == 'select_english' and user_language != 'en':
        db.change_column_value(callback.from_user.id, 'users', 'language', 'en')
        i18n = translator_hub.get_translator_by_locale(locale='en')

    if callback.data == 'select_russian' and user_language != 'ru':
        db.change_column_value(callback.from_user.id, 'users', 'language', 'ru')
        i18n = translator_hub.get_translator_by_locale(locale='ru')

    user_data = db.get_user_data(callback.from_user.id)
    message_content = handle_account_command_or_callback(user_data, i18n)

    await callback.message.edit_text(text=message_content.get('text'),
                                     reply_markup=get_settings_keyboard(message_content.get('keyboard')))


@router.callback_query(F.data.in_(LEVEL_BUTTONS))
async def process_level_button_press(callback: CallbackQuery, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for level selection buttons."""
    user_level = db.get_user_column_data(callback.from_user.id, 'level')

    if user_level != callback.data:
        db.change_column_value(callback.from_user.id, 'users', 'level', callback.data)

    user_data = db.get_user_data(callback.from_user.id)
    message_content = handle_account_command_or_callback(user_data, i18n)

    await callback.message.edit_text(text=message_content.get('text'),
                                     reply_markup=get_settings_keyboard(message_content.get('keyboard')))


@router.callback_query(F.data.in_(TOPIC_BUTTONS))
async def process_topic_button_press(callback: CallbackQuery, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for topic selection buttons."""
    user_topic = db.get_user_column_data(callback.from_user.id, 'topic')

    if user_topic != callback.data:
        db.change_column_value(callback.from_user.id, 'users', 'topic', callback.data)

    user_data = db.get_user_data(callback.from_user.id)
    message_content = handle_account_command_or_callback(user_data, i18n)

    await callback.message.edit_text(text=message_content.get('text'),
                                     reply_markup=get_settings_keyboard(message_content.get('keyboard')))


@router.callback_query(F.data.in_(['next_word', 'next_idiom']))
async def process_next_button_pressed(callback: CallbackQuery, i18n: TranslatorRunner,
                                      db: DatabaseHandler, openai_client: OpenAI):
    """Handler for 'Next' button that generates a new item (word or idiom)."""
    key = 'word'
    if key not in callback.data:
        key = 'idiom'

    attempt_column: str = 'day_' + key
    user_data: dict = db.get_user_data(callback.from_user.id)
    attempts: int = user_data.get(attempt_column)
    user_items = db.get_user_all_items(callback.from_user.id, key)

    if attempts <= 1:
        new_value: dict[str, str] = get_new_word_idiom(openai_client, user_data.get('level'),
                                                       get_topic(user_data.get('topic')), key, user_items)

        while db.check_word_exists_in_column(callback.from_user.id, key, new_value.get('value')):
            new_value = get_new_word_idiom(openai_client, user_data.get('level'), get_topic(user_data.get('topic')),
                                           key, user_items)

        db.register_new_item(callback.from_user.id, key, new_value.get('value'))
        db.change_column_value(callback.from_user.id, 'users', attempt_column, attempts + 1)

        new_text = i18n.get('new-word-idiom-message', item=i18n.get(key), value=new_value.get('value'),
                            meaning=new_value.get('meaning'),
                            example=new_value.get('example'))

        if attempts == 1:
            new_text += '\n\n' + i18n.get('no-more-attempts')
            keyboard = {}
        else:
            new_text += '\n\n' + i18n.get('next-option-message')
            keyboard = {'text': i18n.get('next-button'),
                        'callback': 'next_' + key}

        await callback.message.edit_text(text=new_text,
                                         reply_markup=get_new_word_idiom_keyboard(keyboard, new_value.get('url')))
