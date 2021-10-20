import logging
import schedule
import binance_utils
import messages
import datasource
from bot import bot_updater
from telegram import ParseMode, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters

binance = binance_utils.Binance()
ds = datasource.DataSource()

GET_PAIR, GET_INTERVAL, GET_PRICE = range(3)

# bot start or help
def bot_start(update, context):
    update.message.reply_text(messages.start_bot, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardMarkup(messages.main_menu_keyboard, resize_keyboard = True, selective= True, one_time_keyboard= True))

# support
def donation_and_support_handler(update, context):
    update.message.reply_text(messages.donation_and_support, parse_mode=ParseMode.MARKDOWN_V2)
    
# get current value of a pair
def bot_get_current_value(update, context, pair=0):
    try:
        if pair == 0:
            pair = context.args[0].upper()
        if(binance.check_pair(pair)):
            pair_current_value = float(binance.get_curent_value(pair))
            update.message.reply_text(messages.current_value.format(pair, pair_current_value),parse_mode = ParseMode.MARKDOWN)
        else:
            update.message.reply_text(messages.wrong_pair, parse_mode=ParseMode.MARKDOWN)
    except (IndexError, ValueError):
        update.message.reply_text(messages.not_enough_parameters, parse_mode=ParseMode.MARKDOWN)

# get the last close candle value on specific interval
def bot_get_last_close_candle(update, context, pair=0, interval=0):
    try:
        if pair == 0 and interval == 0:
            pair = context.args[0].upper()
            interval = context.args[1]
        if(binance.check_pair(pair)):
            if(binance.check_interval(interval)):
                last_close_candle_value = float(binance.last_closing_value(pair, interval))
                try:
                    update.message.reply_text(messages.close_candle_value.format(pair,interval,last_close_candle_value), parse_mode=ParseMode.MARKDOWN)
                except:
                    context.bot.editMessageText(chat_id = update.effective_chat.id,
                        message_id=update.callback_query.message.message_id,
                        text=messages.close_candle_value.format(pair,interval,last_close_candle_value),
                        parse_mode = ParseMode.MARKDOWN)
            else:
                update.message.reply_text()
        else:
            update.message.reply_text(messages.wrong_interval, parse_mode=ParseMode.MARKDOWN)
    except (IndexError, ValueError):
        update.message.reply_text(messages.not_enough_parameters, parse_mode=ParseMode.MARKDOWN)

# add sl alert
def bot_register_sl(update, context):
    try:
        chat_id = update.message.chat_id
        pair = context.args[0].upper()
        sl = float(context.args[1])
        interval = context.args[2]
        if(binance.check_pair(pair)):
            if(binance.check_interval(interval)):
                try:
                    ds.add_pair(pair, sl, interval, chat_id)
                    update.message.reply_text(messages.add_sl)
                except:
                    update.message.reply_text(messages.error_message)
            else:
                update.message.reply_text(messages.wrong_interval, parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text(messages.wrong_pair, parse_mode=ParseMode.MARKDOWN)
    except (IndexError, ValueError):
        update.message.reply_text(messages.not_enough_parameters, parse_mode=ParseMode.MARKDOWN)


def check_current_price_handler(update, context):
    update.message.reply_text(messages.choose_pair, parse_mode=ParseMode.MARKDOWN)
    return GET_PAIR

def check_current_price(update, context):
    pair = (update.message.text).upper()
    if binance.check_pair(pair):
        bot_get_current_value(update, context, pair)
        return ConversationHandler.END
    else:
        update.message.reply_text(messages.wrong_pair)
        return GET_PAIR

def check_last_close_value_handler(update, context):
    update.message.reply_text(messages.choose_pair, parse_mode=ParseMode.MARKDOWN)
    return GET_PAIR

def check_last_close_value(update, context):
    # check if we have callback query from interval
    if update.callback_query is None:
        pair = (update.message.text).upper()
        if binance.check_pair(pair):
            # save the chosed pair
            context.user_data['pair'] = pair          
            update.message.reply_text(messages.choose_interval, reply_markup=InlineKeyboardMarkup(messages.interval_keyboard, resize_keyboard = True,selective= True, one_time_keyboard= True))
            return GET_INTERVAL
        else:
            update.message.reply_text(messages.wrong_pair)
            return GET_PAIR
    else:
        query = update.callback_query
        interval = query.data
        pair = context.user_data['pair']
        bot_get_last_close_candle(update, context, pair, interval)
        del context.user_data['pair']
        return ConversationHandler.END

def bot_check_stoploss(interval):
    stoploss_list = ds.check_stoploss(interval)
    try:
        for pair in stoploss_list:
            for id in pair["chat_id"]:
                bot_updater.bot.send_message(chat_id=id, text=messages.stoploss_message.format(pair["pair"], pair["interval"], pair["closing_value"]), parse_mode=ParseMode.MARKDOWN)
    except:
        logging.debug("Can't send message for some reason")

def add_stoploss_handler(update, context):
    update.message.reply_text(messages.choose_pair, parse_mode=ParseMode.MARKDOWN)
    return GET_PAIR

def add_stoploss(update, context, pair=0, interval=0, sl=0):
    # check if we have callback query from interval
    if update.callback_query is None:
        # get pair
        if context.user_data.get('pair') == None:
            pair = (update.message.text).upper()
            if binance.check_pair(pair):
                # save the chosed pair
                context.user_data['pair'] = pair
                update.message.reply_text(messages.choose_interval, reply_markup=InlineKeyboardMarkup(messages.interval_keyboard, resize_keyboard = True,selective= True, one_time_keyboard= True))
                return GET_INTERVAL
            else:
                update.message.reply_text(messages.wrong_pair)
                return GET_PAIR
        # get price 
        else:
            sl = float(update.message.text)
            try:
                ds.add_pair(context.user_data['pair'], sl, context.user_data['interval'], update.message.chat_id)
                update.message.reply_text(messages.add_sl)
                del context.user_data['pair']
                del context.user_data['interval']
                return ConversationHandler.END
            except:
                update.message.reply_text(messages.error_message)
    else:
        query = update.callback_query
        interval = query.data
        context.user_data['interval'] = interval
        # send message to ask for price
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages.choose_price)
        return GET_PRICE

def checksl():
    # 1D
    schedule.every().day.at("00:00").do(bot_check_stoploss, interval='1d')
    print("started 1D schedule")
    # 4h
    schedule.every(4).hours.do(bot_check_stoploss, interval='4h')
    print("started 4H schedule")
    # 1h
    schedule.every().hour.do(bot_check_stoploss, interval='1h')
    print("started 1H schedule")
    # 5m
    schedule.every(5).minutes.do(bot_check_stoploss, interval='5m')
    print("started 5M schedule")

    while True:
        schedule.run_pending()

def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)

simple_handlers = [
    CommandHandler("start", bot_start),
    CommandHandler("get_value", bot_get_current_value),
    CommandHandler("get_close_candle", bot_get_last_close_candle),
    CommandHandler("add_sl", bot_register_sl),
    CommandHandler("help", bot_start),
    MessageHandler(Filters.regex('^🤑 Donation & Support$'), donation_and_support_handler)
]

conversation_handlers = [
    # check current price handler
    ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^📗 Check Current Price$'), check_current_price_handler)],
        states={GET_PAIR:[MessageHandler(Filters.text,check_current_price)]},fallbacks=[],
        allow_reentry=True),
    # check last candle close handler
    ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^📈 Check Last Candle Close Value$'), check_last_close_value_handler)],
        states={
            GET_PAIR:[MessageHandler(Filters.text,check_last_close_value)],
            GET_INTERVAL:[CallbackQueryHandler(check_last_close_value)]                      
        },
        fallbacks=[],
        allow_reentry=True),
    # add sl reminder handler
    ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^🚧 Add StopLoss Alert$'), add_stoploss_handler)],
        states={
            GET_PAIR:[MessageHandler(Filters.text, add_stoploss)],
            GET_INTERVAL:[CallbackQueryHandler(add_stoploss)],
            GET_PRICE:[MessageHandler(Filters.text, add_stoploss)]                    
        },
        fallbacks=[],
        allow_reentry=True),
]