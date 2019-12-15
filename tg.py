from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler

def start_tg_bot(tk='1047503404:AAEFj_6ueKn_i2iBLZctTfWXmJyrf68Q9ts'):
    updater = Updater(token=tk, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a DoorbellCamera bot!")
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    return None

#def send_text(
