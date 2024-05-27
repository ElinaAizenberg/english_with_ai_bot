from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


def create_translator_hub() -> TranslatorHub:
    """Create TranslatorHub by locales for English and Russion versions of the bot."""
    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en", "ru")
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=["bot/locales/ru/messages.ftl", "bot/locales/ru/buttons.ftl",
                               "bot/locales/ru/utils.ftl", "bot/locales/ru/help.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["bot/locales/en/messages.ftl", "bot/locales/en/buttons.ftl",
                               "bot/locales/en/utils.ftl", "bot/locales/en/help.ftl"]))
        ],
    )
    return translator_hub
