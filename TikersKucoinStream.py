import websockets
import asyncio
import json
import requests
import certifi, os
import time
import threading
import api_keys


class TickersKucoinWebsocket:
    def __init__(self, min_trading_volume: float = None):
        os.environ['SSL_CERT_FILE'] = certifi.where()
        self.ticker_list_kucoin = {}
        self.__uuid = "kucoin2023"
        self.__min_trading_volume = min_trading_volume


    def __get_all_tickers(self) -> list:
        base_url = "https://api.kucoin.com"
        all_tickers_url = "/api/v1/market/allTickers"
        response = requests.get(base_url + all_tickers_url)
        if response.status_code == 200:
            data = response.json()
            if self.__min_trading_volume != None:
                symbols = [ticker['symbol'] for ticker in data['data']['ticker'] if ticker['symbol'].endswith('USDT')
                            and not ticker['symbol'].endswith(('2S-USDT', '2L-USDT', '3S-USDT', '3L-USDT', '5S-USDT', '5L-USDT'))
                            and float(ticker['volValue']) > self.__min_trading_volume]
            
            else:
                symbols = [ticker['symbol'] for ticker in data['data']['ticker'] if ticker['symbol'].endswith('USDT')
                            and not ticker['symbol'].endswith(('2S-USDT', '2L-USDT', '3S-USDT', '3L-USDT', '5S-USDT', '5L-USDT'))]
                
            symbols_lists = [symbols[i:i+100] for i in range(0, len(symbols), 100)]
            return symbols_lists
        
        else:
            print("Error when getting list of Kucoin exchange tickers:", response.status_code)


    def __get_token_ws(self):
        url = "https://api.kucoin.com/api/v1/bullet-public"
        response = json.loads(requests.post(url).text)
        token = response['data']['token']
        return token


    async def __kucoinws(self, ws, symbol_list):
        msg = {
            "id": "%s" % (self.__uuid),
            "type": "subscribe",
            "topic": "/market/ticker:" + ','.join(symbol_list),
            "response": True
        }
        msg = json.dumps(msg)
        await ws.send(msg)

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                self.ticker_list_kucoin[data['topic'].split(":")[1].replace("-", "")] = float(data['data']['price'])
      
            except Exception as e:
                # print(f"[Kucoin]Error processing message: {str(e)}")
                pass

    async def __connect_to_kucoin_ws(self, symbol_list):
        async with websockets.connect(f"wss://ws-api-spot.kucoin.com/?token={self.__get_token_ws()}&[connectId={self.__uuid}]") as ws:
            await self.__kucoinws(ws, symbol_list)


    def __start_connection(self, symbol_list):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.__connect_to_kucoin_ws(symbol_list))
        loop.run_forever()


    def ticker_stream_start(self):
        symbol_lists = self.__get_all_tickers()
        for symbol_list in symbol_lists:
            threading.Thread(target=self.__start_connection, args=(symbol_list,), daemon=True).start()


    

# ws = TickersKucoinWebsocket(api_keys.min_trading_volume)
# ws.ticker_stream_start()

# while True:
#     time.sleep(4)
#     print(ws.ticker_list_kucoin, len(ws.ticker_list_kucoin))
#     print('\n')
#     print(len(ws.ticker_list_kucoin))