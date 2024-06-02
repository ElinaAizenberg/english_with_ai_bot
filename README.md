# Telegram Bot: Practice English with AI
<a href="https://t.me/english_with_art_bot">Telegram bot</a>  that helps users practice new vocabulary in English with the help of GPT-4 and DALL-E 3 models.

## Description
User starts subscription pressing <b>Start</b> button.

<img src="https://github.com/ElinaAizenberg/english_with_ai_bot/assets/77394738/7e267643-6367-47a1-826b-c7cfbf285bb8" width="400">


The <b>/start</b> command gives a short description of what this bot can do.

In order to activate an account and receive the first set of new vocabulary, user needs to send the <b>/activate</b> command. Beforehand, user can check and change settings with the <b>/account</b> command.
<i>While the account is not activated, user won’t receive messages with new vocabulary.</i>

<b>New Vocabulary Every Day</b>

Every day at 9 o’clock (UTC time), user receives 2 messages: a word and an idiom.

<img src="https://github.com/ElinaAizenberg/english_with_ai_bot/assets/77394738/2c7c76ec-79d0-4980-bff9-8b92e9993e10" width="400">

Each message contains an explanation of meaning and an example. Also, each message has 2 buttons:
- Link to the Cambridge dictionary page
- Next

User can click ‘Next’ if User is already familiar with a word/idiom and want to get another one. User has <b>3 options per day</b> for both new words and idioms. In other words, User can click ‘Next’ 2 times for each message.

<b>Generate Images and Check Grammar</b>

User can send examples with new vocabulary to the bot by starting the message with the <b>/check</b> command. For example:
<b>/check</b> A jury found unanimously that there was proof of her guilt beyond a reasonable doubt.

An example should be a complete sentence that the bot will find coherent (not a random set of words) with new vocabulary used. Otherwise, it will ask user to provide another example.

<img src="https://github.com/ElinaAizenberg/english_with_ai_bot/assets/77394738/59a18dc9-70ff-4541-ac44-58574c962f1e" width="400">

The bot will check the grammar, spelling, and return a corrected version if needed, as well as generate an image based on provided example and the amount of earned points.
User has <b>2 available checks per day</b>. In other words, sser can generate 2 images per day.
If user clicked the ‘Next’ button, the latest provided item of new vocabulary should be used in examples.


<b>Subscription</b>

Every new user gets <b>7 days of a free trial period</b>. When it’s over, the user’s account is frozen. It can be reactivated with payment for further subscription or with one of the promo codes.

<b>Account</b>
User can check account settings with the <b>/account</b> command (in the main menu):
- Status
- Level (A1,...,C2)
- Topic
- Language of the bot (Russian or English)

<img src="https://github.com/ElinaAizenberg/english_with_ai_bot/assets/77394738/408d4eb9-ee07-4ed9-98f1-7aa0547d9d90" width="400">

Also, user can change these parameters with respective buttons under the message with the account summary.
More information about levels in English is <a href="https://learnenglish.britishcouncil.org/english-levels/understand-your-english-level">here</a>.

<b>Points</b>

User can earn points by sending examples with new vocabulary to the bot.
If user uses one new word or idiom in the sentence, it gives <b>1 point</b>; both word and idiom - <b>2 points</b>.
If user sends an example for checking without any new vocabulary, user will lose 1 point (if the balance is not zero).
User can check account points balance with the <b>/points</b> command (in the main menu).

<b>Vocabulary</b>

User can check all words and idioms saved for account sending the command with the <b>/vocabulary</b> command.


## Localization

<a href="https://t.me/english_with_art_bot">Practice English with AI</a> supports multiple languages, making it accessible to a broader audience. Currently, all messages and buttons can be displayed in English or Russian. The bot is internationalized using the fluentogram library, allowing for easy expansion to additional languages.

<b>Adding a new language</b>

If you wish to add support for a new language, follow these steps:

1. create localization files - a set of .ftl files (check directories /bot/locales/en or /bot/locales/ru);
2. place these files in /bot/locales/new_language directory;
3. modify the <b>create_translator_hub()</b> function to include the new language:
   - add a new map to TranslatorHub
   - create a translator FluentTranslator 


## Structure
## Run Telegram bot
### Requirements
### Env. variables
### Docker


