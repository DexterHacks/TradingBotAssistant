from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton


start_bot = """
🤖 Hello and welcome to your Trading Bot Assistant 🤖
        **Am here to help you with your tradings**

Please choose one of the following options on the __keyboard layout__ or use __inline commands__:
📙 start the bot or restart it:
```
    /start
```

📕 to get current pair value:
```
    /get_value PAIR_NAME 
    Example: /get_value btcusdt
```

📗 to get the last closing candle on a specific interval
```
    /get_close_candle PAIR_NAME Interval
    Example: /get_close_canlde btcusdt 5m
```

📘 to add a stoploss reminder on specific time interval:
```
    /add_sl PAIR_NAME StopLoss Interval  
    Example: /add_sl btcusdt 50000 4h
```

By the way, am still in my early stages 
my coder is @Loay\\_H , all suggestions and ideas to improve me are welcome
"""

wrong_pair = "✖️ Wrong pair, please enter a pair that exists in binance platform\nExample: `btcusdt` , `ethbusd` , `solbtc` , ... :"

wrong_interval = "✖️ Wrong interval, please enter a valid interval\n valid intervals are:\n- `1d`\n- `4h`\n- `1h`\n- `5m`"

not_enough_parameters = "✖️ Not enough arguments, review /help for examples on how to use the bot"

current_value = "📗 `{0}`: {1:g}"

close_candle_value = "📗 `{0}` last close value on `{1}` interval: {2:g}"

choose_interval = "⏳ Please choose one of the following intervals:"

choose_pair = "📄 Please enter the pair you want\nExample: `btcusdt` , `ethbusd` , `solbtc` , ... :"

choose_price = "📄 Please enter the stoploss price: "

stoploss_message = "🛑 stoploss reached for `{0}` on interval `{1}` with a closing value of {2}"

error_message = "❌ there was an error, please try again or contact the coder to report bugs"

add_sl = "✅ your stoploss alert has been added successfully "

donation_and_support = """
🎉🎉 Thank you for considering to support this project 🎉🎉

BTC Address
```
bc1qd82uvm3u8uu7xuvvwl0wpz208wv3387c3ju7jk
```

USDT Address
```
0x87Ca23945cD4A2D296E07E20a0e4C7ACDf92e205
```
"""
main_menu_keyboard = [
        ["📗 Check Current Price"],
        ["📈 Check Last Candle Close Value"],
        ["🚧 Add StopLoss Alert"],
        ["🤑 Donation & Support"]
]

interval_keyboard = [
    [InlineKeyboardButton("📗 5m", callback_data="5m"),InlineKeyboardButton("📗 1h", callback_data="1h")],
    [InlineKeyboardButton("📗 4h", callback_data="4h"),InlineKeyboardButton("📗 1d", callback_data="1d")]]