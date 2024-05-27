MENU_COMMANDS_EN: dict[str, str] = {
    '/account': 'check and update settings',
    '/points': 'show total earned points',
    '/help': 'show information about this bot',
    '/contact': 'contact the developer',
}

LEVEL_BUTTONS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
TOPIC_BUTTONS = ['general', 'art', 'social', 'culture', 'tech']

TOPICS = {
    'social': 'Law, Economics, Social studies',
    'art': 'Art, Literature, Cinema',
    'tech': 'Science, Technology',
    'culture': 'History, Travelling, Religion',
    'general': 'Daily life'
}


def get_topic(topic_key: str) -> str:
    """Get full topic description in English by key. If key is not present, topic - Daily life."""
    if topic_key in TOPICS.keys():
        return TOPICS.get(topic_key)

    return TOPICS.get('general')

