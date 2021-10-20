from binance.client import Client
import os

class Binance:
    # Binance API Init 
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')

    # intervals
    global accepted_pairs, accepted_intervals
    accepted_intervals = ("5m", "1h", "4h", "1d")
    accepted_pairs = ('USDT', 'USDC', 'BNB', 'BTC', 'ETH')

    def __init__(self) -> None:
        self.client = Client(self.api_key, self.api_secret)

    # Get current pair value
    def get_curent_value(self, pair):
        return  self.client.get_symbol_ticker(symbol=pair)['price'] 

    # Check if pair is valid
    def check_pair(self, pair):
        if pair.upper().endswith(accepted_pairs):
            return True
        else:
            return False

    # Check if interval is valid
    def check_interval(self, interval):
        if interval in accepted_intervals:
            return True
        else:
            return False

    # Test if there is connection to binance 
    def check_connection(self):
        try:
            self.client.ping()
        except:
            return False
        finally:
            return True

    # Get the last closing value candle according to the given interval
    def last_closing_value(self, pair, interval):
        if interval == "1m":
            close_value = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_1MINUTE, "2 Minute ago UTC")[0][4]
        elif interval == "5m":
            close_value = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_5MINUTE, "10 Minute ago UTC")[0][4]
        elif interval == "1h":
            close_value = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "2 Hour ago UTC")[0][4]
        elif interval == "4h":
            close_value = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_4HOUR, "8 Hour ago UTC")[0][4]
        elif interval == "1d":
            close_value = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_1DAY, "2 Day ago UTC")[0][4]
        return close_value

