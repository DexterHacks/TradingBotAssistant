#!/usr/bin/env python
import logging
from telegram.ext import Updater
import handlers
import os
from threading import Thread

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot_updater = Updater(token=BOT_TOKEN, use_context=True)

def main():
    # HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
    # PORT = os.getenv('PORT')

    # initiate telegram bot

    # Get the dispatcher to register handlers
    dispatcher = bot_updater.dispatcher

    for handler in handlers.simple_handlers:
        dispatcher.add_handler(handler)
    
    for handler in handlers.conversation_handlers:
        dispatcher.add_handler(handler)

    dispatcher.add_error_handler(handlers.error)

    check_sl_thread = Thread(target=handlers.checksl, daemon=True)
    
    # Start the Bot
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=BOT_TOKEN,
    #                       webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}")
    bot_updater.start_polling()
    check_sl_thread.start()

    bot_updater.idle()


if __name__ == '__main__':
    main()
