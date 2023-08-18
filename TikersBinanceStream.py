from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from time import sleep
import certifi
import os
import json
import logging
import api_keys

import time

logging.getLogger("unicorn_binance_websocket_api")
logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

class TikersBinanceWebsocket:
    def __init__(self, api_key: str, api_secret: str) -> None:
        os.environ['SSL_CERT_FILE'] = certifi.where()
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com")
        self.tiker_list = {}

    def miniTicker_arr_start(self):
        def process_new_receives_miniTicker(stream_data, stream_buffer_name=False):
            stream_dat = json.loads(stream_data)
            results = [(item['s'], item['c']) for item in stream_dat if 's' in item and 'c' in item]
            for symbol, price in results:
                self.tiker_list[symbol] = float(price)

        self.binance_websocket_api_manager.create_stream("arr", "!miniTicker", process_stream_data=process_new_receives_miniTicker)


# ws = TikersBinanceWebsocket(api_keys.API_KEY_BINANCE, api_keys.API_SECRET_BINANCE)
# ws.miniTicker_arr_start()
# while True:
#     print(ws.tiker_list)
#     print(len(ws.tiker_list))
#     time.sleep(5)


