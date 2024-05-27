import json
import logging
from openai import OpenAI
from openai import OpenAIError


logger = logging.getLogger(__name__)


def get_new_word_idiom(openai_client: OpenAI, level: str, topic: str, source: str, assistant_comment: str = "") -> dict:
    """
    Generate a dictionary for a new item (word or idiom) tailored for level and topic with following keys:
    - value;
    - meaning;
    - example;
    - url to the value on Cambridge dictionary website.
    """
    user_message: str = (f"Provide a example of an English {source} with following parameters: "
                         f"level - {level}, topic - {topic}."
                         f"The answer should be JSON with the keys: 'value', 'meaning', "
                         f"'example'(an example of using this word/idiom), "
                         f"'url'(link to this word/idiom on Cambridge dictionary website).")
    messages = [
        {"role": "system", "content": "You are an experienced British English teacher who specializes in tutoring "
                                      "students for Cambridge English exams (all levels)."},
        {"role": "user", "content": user_message}
    ]
    if assistant_comment:
        items_list = assistant_comment.replace('|', ', ')
        messages.append({'role': "assistant",
                         "content": f"{source} should not be used in the list: {items_list.lower()}"})

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        max_tokens=400,
        response_format={"type": "json_object"},
        messages=messages
    )
    json_response = json.loads(completion.choices[0].message.content)

    return json_response


def check_sentence_for_new_words(openai_client: OpenAI, sentence: str, new_words: list[str]) -> list[str]:
    """Check if the sentence from a user actually contains any of new vocabulary set: word and idiom."""
    booleans_list: list[str] = list()

    for item in new_words:
        user_message: str = (f"Check if '{item}' is used in the line."
                             f"Line: '{sentence.replace('/check ', '')}'."
                             f"Even if there are grammar mistakes in how '{item}' is used, it counts for being used."
                             f"Return output in the boolean format: "
                             f"True (when it is used in the line) or False (it's not used in the line).")

        messages = [
            {"role": "system", "content": "You are an experienced British English teacher who specializes in tutoring "
                                          "students for Cambridge English exams (all levels)."},
            {"role": "user", "content": user_message},
        ]

        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            temperature=0.5,
            max_tokens=450,
            messages=messages
        )
        booleans_list.append(completion.choices[0].message.content)

    return booleans_list


def check_sentence_purpose(openai_client, sentence: str) -> bool:
    """Check if a sentence from a user is actually a sentence and not a command or random set of words."""
    user_message: str = (f"Check if the line looks like a complete sentence and has coherence."
                         f"Line: '{sentence.replace('/check ', '')}'."
                         f"The line might have grammar or spelling mistakes, starts with lower case letter, "
                         f"not have full stop at the end, "
                         f"but it should not be taken into account for you judgement."
                         f"Return output in the boolean format: "
                         f"True (when a line looks like a sentence) or "
                         f"False (when a line doesn't look like a regular sentence)."
                         )

    messages = [
        {"role": "system", "content": "You are an experienced British English teacher who specializes in tutoring "
                                      "students for Cambridge English exams (all levels)."
                                      "Your student has to come up with an example to practice new vocabulary,"
                                      "but he or she might be cheating by providing a simple word, command or "
                                      "collocation which purpose is solely to pass the check that they used new words."
                                      "Your goal is to catch cheating."
         },

        {"role": "user", "content": user_message}
    ]

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        max_tokens=500,
        messages=messages
    )
    response = completion.choices[0].message.content

    return True if response.lower() == 'true' else False


def check_sentence_grammar(openai_client, sentence: str):
    """Check grammar, spelling in a sentence from a user and provide a corrected version if needed."""
    user_message: str = (f"Check if the sentence grammatically correct."
                         f"If there are errors, provide also the correct version. Sentence: {sentence.replace('/check ', '')}")
    messages = [
        {"role": "system", "content": "You are an experienced British English teacher who specializes in tutoring "
                                      "students for Cambridge English exams (all levels)."
                                      "You also have basic understanding of HTML."},

        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "Answer format: short conclusion whether the sentence is correct or not (please, be kind and supportive)."
                                         "If you provide corrected version of the sentence,"
                                         "bold changed parts with '<b>' and '</b>'."
                                         "Do not ask back any questions!"}
    ]

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=450,
        messages=messages
    )

    return completion.choices[0].message.content


def generate_image(openai_client, sentence: str) -> str | None:
    """Generate an image using a sentence from a user."""
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=sentence,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        return image_url

    except OpenAIError as e:
        logger.error(f"Caught BadRequestError: {e}")
        return None


