import logging
from openai import AsyncOpenAI
import openai
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['telegram_bot_token']
ALLOWED_USER_IDS = config['allowed_user_ids']
VERIFICATION_TOKEN = config['verification_token']
OPENAI_API_KEY = config['openai_api_key']

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ALLOWED_USER_IDS:
        await update.message.reply_text('Hello, master!')
    else:
        await update.message.reply_text('Sorry, you are not authorized to use this bot.')

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) > 0:
        token = args[0]
        if token == VERIFICATION_TOKEN:
            await update.message.reply_text('Verification successful. Please send your Telegram user ID to be added to the list of authorized users.')
            context.user_data['is_verifying'] = True
        else:
            await update.message.reply_text('Verification failed. Please check your token and try again.')
    else:
        await update.message.reply_text('Please send your verification token using /verify <your_token_here>.')

async def openai_query(user_message):
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_message},
            ],
            model="gpt-3.5-turbo-1106",
        )
        return chat_completion.choices[0].message.content 
    except openai.RateLimitError:
        return "I'm currently overwhelmed with requests. Please try again later."
    except openai.APIError as error:
        logging.error(f"An OpenAI API error occurred: {error}")
        return "Sorry, I encountered an API error. Please try again."
    except Exception as error:
        logging.error(f"An unexpected error occurred: {error}", exc_info=True)
        return "Sorry, I encountered an unexpected error. Please try again."


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('is_verifying', False):
        try:
            user_id = int(update.message.text)
            if user_id not in ALLOWED_USER_IDS:
                ALLOWED_USER_IDS.append(user_id)
                with open('config.json', 'w') as config_file:
                    json.dump({'telegram_bot_token': TOKEN, 'allowed_user_ids': ALLOWED_USER_IDS, 'verification_token': VERIFICATION_TOKEN}, config_file)
                await update.message.reply_text('Your user ID has been added to the list of authorized users.')
            else:
                await update.message.reply_text('This user ID is already in the list of authorized users.')
            context.user_data['is_verifying'] = False
        except ValueError:
            await update.message.reply_text('Invalid user ID. Please send a valid Telegram user ID.')
    else:
        user_message = update.message.text
        openai_response = await openai_query(user_message)
        await update.message.reply_text(openai_response)
        pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "This bot allows specific authorized users to interact with it. Use /start to initiate interaction, /verify with your token to verify yourself, and /restart to restart the bot interaction. Ensure you're authorized to use these commands."
    await update.message.reply_text(help_text)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

    application.run_polling()

if __name__ == '__main__':
    main()