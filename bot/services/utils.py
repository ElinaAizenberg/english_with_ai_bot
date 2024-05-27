from aiogram import Bot
from fluentogram import TranslatorRunner
from datetime import datetime, timezone


ACTIONS = {'new_user': ' started the bot.',
           'user_blocked': ' blocked the bot.',
           'admin_command': ' tried to call admin command.'}


def handle_account_command_or_callback(user_data: dict[str, str], i18n: TranslatorRunner) -> (
        dict)[str, str | dict[str, str]]:
    """Create text message and keyboard buttons' names for /account command or /back button/action."""
    if user_data.get('status') == 1:
        user_status = i18n.get('active-status')
    elif user_data.get('status') == 2:
        user_status = i18n.get('frozen-status')
    else:
        user_status = i18n.get('deactive-status')

    user_topic = i18n.get(user_data.get('topic') + '-topic')
    user_level = user_data.get('level')
    user_language = i18n.get('language')

    text = i18n.get('account-summary-message',
                    status=user_status,
                    level=user_level,
                    topic=user_topic,
                    language=user_language)

    keyboard = {'language': i18n.get('language-button'),
                'level': i18n.get('level-button'),
                'topic': i18n.get('topic-button'),
                'close': i18n.get('close-button')
                }

    return {'text': text, 'keyboard': keyboard}


def check_user_status(user_subscription_end: datetime) -> bool:
    """Check if user's end of subscription is later than current time (UTC)."""
    current_utc_time = datetime.now(timezone.utc)
    end_utc_time = user_subscription_end.replace(tzinfo=timezone.utc)

    if current_utc_time <= end_utc_time:
        return True
    else:
        return False


async def notify_admin(bot: Bot, admins: list[int], full_name: str, action: str):
    """Notify admin when a user performs one of the ACTIONS."""
    if admins:
        text = full_name + ACTIONS.get(action)
        await bot.send_message(admins[0], text=text)


def construct_promo_code() -> str:
    """Construct currently valid promo-code of the format: BAYMAX{MM}{YYYY}"""
    current_date = datetime.now(timezone.utc)

    month = current_date.strftime("%m")
    year = current_date.strftime("%Y")

    promo_code = f"BAYMAX{month}{year}"

    return promo_code
