import logging
from aiogram import Router
from aiogram.types import Message, URLInputFile
from aiogram.filters import Command
from aiogram.enums import ChatAction
from openai import OpenAI
from fluentogram import TranslatorRunner
from datetime import datetime, timezone, timedelta

from bot.filters.filters import (UserExists, UserActivated, UserNonActivated,
                                 UserFrozen, UserAvailableChecks, NewWordIdiomUsed)
from bot.keyboards.keyboards import (get_language_keyboard, get_new_word_idiom_keyboard,
                                     get_contact_developer_keyboard, get_settings_keyboard)
from bot.services.utils import notify_admin, handle_account_command_or_callback, construct_promo_code
from bot.services.openai import get_new_word_idiom, check_sentence_purpose, check_sentence_grammar, generate_image
from bot.lexicon.lexicon import get_topic
from bot.database.database_handler import DatabaseHandler


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command(commands="start"), ~UserExists())
async def process_start_new_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler, admins: list[int]):
    """Handler for /start command and new users. Register a new user in the database."""
    text = i18n.get('start-new-user', username=message.from_user.full_name)
    text += "\nPlease, select the language: \nПожалуйста, выберите язык:"
    await message.answer(text=text, reply_markup=get_language_keyboard())

    db.add_user(message.from_user.id)
    await notify_admin(message.bot, admins, message.from_user.full_name, 'new_user')


@router.message(Command(commands="start"), UserExists())
async def process_start_old_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for /start command and old (returning) users."""
    user_data = db.get_user_data(message.from_user.id)
    points = user_data.get('points')
    status = user_data.get('status')
    if status == 1:
        user_status = i18n.get('active-status')
    elif status == 2:
        user_status = i18n.get('frozen-status')
    else:
        user_status = i18n.get('deactive-status')

    text = i18n.get('start-old-user', username=message.from_user.full_name)
    text += '\n' + i18n.get('old-user-status', status=user_status)
    text += '\n' + i18n.get('points-status', points=points)

    await message.answer(text=text)
    await message.answer(text=i18n.get('short-description-message'))


@router.message(Command(commands=["activate", "check"]), UserFrozen())
async def process_frozen_user_activate_command(message: Message, i18n: TranslatorRunner):
    """Handler for /activate and /chck commands when user's status is 'frozen'."""
    text = i18n.get('activate-frozen-command')
    await message.answer(text=text)


@router.message(Command(commands="activate"), UserActivated())
async def process_activated_user_activate_command(message: Message, i18n: TranslatorRunner):
    """Handler for /activate command when user's status is 'activated'."""
    text = i18n.get('activate-old-account')
    await message.answer(text=text)


@router.message(Command(commands="activate"), UserNonActivated())
async def process_activate_command(message: Message, i18n: TranslatorRunner,
                                   db: DatabaseHandler, openai_client: OpenAI):
    """
    Handler for /activate command when user's status is 'non-activated'.
    Change the status to 'activated', generate and send a new vocabulary set: word + idiom.
    """

    text = i18n.get('activate-new-account')
    await message.answer(text=text)

    db.change_column_value(message.from_user.id, 'users', 'status', '1')
    level = db.get_user_column_data(message.from_user.id, 'level')
    topic_key = db.get_user_column_data(message.from_user.id, 'topic')

    for item_name in ['word', 'idiom']:
        new_item = get_new_word_idiom(openai_client, level, get_topic(topic_key), item_name)
        db.register_new_item(message.from_user.id, item_name, new_item.get('value'))

        new_text = i18n.get('new-word-idiom-message', item=i18n.get(item_name), value=new_item.get('value'),
                            meaning=new_item.get('meaning'),
                            example=new_item.get('example'))
        new_text += '\n\n' + i18n.get('next-option-message')
        keyboard = {'text': i18n.get('next-button'), 'callback': 'next_' + item_name}

        await message.answer(text=new_text,
                             reply_markup=get_new_word_idiom_keyboard(keyboard, new_item.get('url')))


@router.message(Command(commands="points"))
async def process_points_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for /points command."""
    user_points = db.get_user_column_data(message.from_user.id, 'points')
    text = i18n.get('points-status', points=user_points)
    await message.answer(text=text)


@router.message(Command(commands="help"))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    """Handler for /help command."""
    text = i18n.get('help-message')
    await message.answer(text=text)


@router.message(Command(commands="contact"))
async def process_contact_command(message: Message, i18n: TranslatorRunner, admins: list[int]):
    """Handler for /contact command."""
    admin_id: str = admins[0]
    await message.answer(text=i18n.get('contact-developer-message'),
                         reply_markup=get_contact_developer_keyboard(i18n.get('developer-button'), admin_id))


@router.message(Command(commands="account"))
async def process_account_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for /account command."""
    user_data = db.get_user_data(message.from_user.id)
    message_content = handle_account_command_or_callback(user_data, i18n)

    await message.answer(text=message_content.get('text'),
                         reply_markup=get_settings_keyboard(message_content.get('keyboard')))


@router.message(Command(commands="check"), UserNonActivated())
async def process_non_activated_check_command(message: Message, i18n: TranslatorRunner):
    """Handler for /check command and is user's status is 'non-activated'."""
    text = i18n.get('non-active-user')
    text += '\n' + i18n.get('activate-message')
    await message.answer(text=text)


@router.message(Command(commands="check"), ~UserAvailableChecks())
async def process_redundant_check_command(message: Message, i18n: TranslatorRunner):
    """Handler for /check command, user's status is 'activated', but user doesn't have daily available checks."""
    text = i18n.get('no-available-checks')
    await message.answer(text=text)


@router.message(Command(commands="check"), UserAvailableChecks(), NewWordIdiomUsed())
async def process_check_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler,
                                words_used: int, openai_client: OpenAI):
    """
    Handler for /check command, user's status is 'activated', user has daily available checks and used new vocabulary.
    Check if the sentence makes sense, check grammar and spelling and generate an image.
    """
    text: str = ''
    if words_used == 0:
        text = i18n.get('no-word-idiom-used')

        if db.plus_minus_points(message.from_user.id, -1):
            text += '\n' + i18n.get('minus-one-point')

    else:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        if check_sentence_purpose(openai_client, message.text):
            if words_used == 1:
                db.plus_minus_points(message.from_user.id, 1)
                text = i18n.get('plus-one-point')

            if words_used == 2:
                db.plus_minus_points(message.from_user.id, 2)
                text = i18n.get('plus-two-points')

            text += '\n' + check_sentence_grammar(openai_client, message.text)
            await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO, )
            image_url = generate_image(openai_client, message.text)
            if image_url:
                photo = URLInputFile(image_url)
                await message.answer_photo(photo=photo)
                db.increment_user_checks(message.from_user.id)
            else:
                await message.answer(text=i18n.get('bad-request-message'))

        else:
            text = i18n.get('provide-another-example')

    await message.answer(text=text)


@router.message(Command(commands="promo"))
async def process_promo_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler):
    """
    Handler for /promo command.
    Check if promo-code is valid, if yes - postpone end of subscription time by 30 days.
    """
    current_promo_code = construct_promo_code()
    if current_promo_code in message.text:
        status = db.get_user_column_data(user_id=message.from_user.id, column_name='status')
        if status != 1:
            db.change_column_value(message.from_user.id, 'users', 'status', 1)

        current_utc_time = datetime.now(timezone.utc)
        subscription_end = current_utc_time + timedelta(days=30)
        time_string = subscription_end.strftime("%Y-%m-%d %H:%M:%S")
        db.change_column_value(message.from_user.id, 'users', 'subscription_end', time_string)

        text = i18n.get('promo-code-activated')

    else:
        text = i18n.get('promo-code-not-valid')

    await message.answer(text=text)


@router.message(Command(commands="vocabulary"))
async def process_vocabulary_command(message: Message, i18n: TranslatorRunner, db: DatabaseHandler):
    """Handler for /vocabulary command that returns all registered words/idioms per user."""

    for item in ['word', 'idiom']:
        user_items = db.get_user_all_items(message.from_user.id, item)
        if user_items:
            items_list = user_items.split('|')
            text_key = f"all-{item}-in-database"
            text = i18n.get(text_key)
            for i in items_list:
                text += '\n' + '- ' + i

        else:
            text_key = f"no-{item}-in-database"
            text = i18n.get(text_key)

        await message.answer(text=text)
