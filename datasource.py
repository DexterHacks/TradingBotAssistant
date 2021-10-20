#!/usr/bin/env python
from pymongo import MongoClient 
import binance_utils

class DataSource:
    CONNECTION_STRING = "mongodb+srv://learn-user:YLElEXxxVcyouHvF@tradingassistantbot.an44v.mongodb.net/TradingAssistantBot?retryWrites=true&w=majority"
    binance = binance_utils.Binance()
    def __init__(self) -> None:
        self.client = MongoClient(self.CONNECTION_STRING)
        self.database = self.client["TradingAssistantBot"]
        self.collection = self.database["stoploss_pairs_data"]

    def testdb(self):
        if self.database.get_collection():
            return True
        else:
            return False
        
    def add_pair(self, pair, sl, interval, chat_id):
        query_pair_interval_sl = {"pair": pair, "interval": interval, "stoploss": sl}
        insert_new_document = {"pair": pair, "interval": interval, "stoploss": sl, "chat_id": [chat_id], "trigger_count": 0}
        push_chat_id = {"$push": { "chat_id": chat_id }}

        # check if document already exists
        if self.collection.find(query_pair_interval_sl).count() != 0:
            self.collection.update(query_pair_interval_sl, push_chat_id)
        else:
            self.collection.insert_one(insert_new_document)

    def get_interval(self, interval):
        query_interval = {"interval": interval}
        return self.collection.find(query_interval)
    
    def increment_trigger(self, pair, sl, interval):
        query_pair_interval_sl = {"pair": pair, "interval": interval, "stoploss": sl}
        increment = {"$inc": {"trigger_count": 1}}
        self.collection.update(query_pair_interval_sl, increment)

    def check_stoploss(self, interval):
        uniq_pairs = self.get_interval(interval).distinct("pair")
        stoploss = []
        for uniq_pair in uniq_pairs:
            uniq_pair_instances = self.collection.find({"pair": uniq_pair, "interval": interval})
            pair_closing_value = float(self.binance.last_closing_value(uniq_pair, interval))
            for pair in uniq_pair_instances:
                if pair_closing_value < pair["stoploss"]:
                    append_data = {"pair": pair["pair"], "stoploss": pair["stoploss"], "closing_value":pair_closing_value, "chat_id": pair["chat_id"], "interval": pair["interval"]}
                    self.collection.delete_one(pair)
                    stoploss.append(append_data)
                    self.increment_trigger(pair["pair"], pair["stoploss"], interval)
        return stoploss