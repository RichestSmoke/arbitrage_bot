from pybit.unified_trading import WebSocket, HTTP
import certifi, os
import threading
import api_keys
import time


class TikersBybitWebsocket:
    def __init__(self, api_key: str, api_secret: str, min_trading_volume: float = None) -> None:
        os.environ['SSL_CERT_FILE'] = certifi.where()
        self.tiker_list_bit = {}
        self.__min_trading_volume = min_trading_volume
    
        self.session = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret)


    def __get_tickers(self):
        data = self.session.get_tickers(category="spot")
        if self.__min_trading_volume != None:
            symbols = [item['symbol'] for item in data['result']['list'] if item['symbol'].endswith('USDT') 
                        and not item['symbol'].endswith(('2SUSDT', '2LUSDT', '3SUSDT', '3LUSDT')) 
                        and float(item['turnover24h']) > self.__min_trading_volume]
        else:
            symbols = [item['symbol'] for item in data['result']['list'] if item['symbol'].endswith('USDT') 
                        and not item['symbol'].endswith(('2SUSDT', '2LUSDT', '3SUSDT', '3LUSDT'))]

        symbols_lists = [symbols[i:i+10] for i in range(0, len(symbols), 10)]
        return symbols_lists

    def __create_ticker_stream(self):
        symbols_lists = self.__get_tickers()
        ws = WebSocket(testnet=False, channel_type="spot")

        def handle_message(message):
            data = message['data']
            self.tiker_list_bit[data['symbol']] = float(data['lastPrice'])
            # print(f"{data['symbol']} = {data['lastPrice']}")

            
        for ticker_list in symbols_lists:
            ws.ticker_stream(symbol=ticker_list, callback=handle_message)

        while True:
            time.sleep(1)
    
    def ticker_stream_start(self):
        threading.Thread(target=self.__create_ticker_stream).start()


# ws = TikersBybitWebsocket(api_keys.API_KEY_BIT, api_keys.API_SECRET_BIT, api_keys.min_trading_volume)
# ws.ticker_stream_start()

# while True:
#     print(ws.tiker_list_bit, len(ws.tiker_list_bit))
#     time.sleep(5)

