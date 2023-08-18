import websockets
import asyncio
import json
import requests
import certifi, os
import time
import threading
import api_keys

# GET /api/v1/currencies 
# "isWithdrawEnabled": true,
#     "isDepositEnabled": true,

class TickersOKXWebsocket:
    def __init__(self, min_trading_volume: float = None):
        os.environ['SSL_CERT_FILE'] = certifi.where()
        self.ticker_list_okx = {}
        self.__min_trading_volume = min_trading_volume


    def __get_all_tickers(self) -> list:
        base_url = "https://www.okx.com"
        all_tickers_url = "/api/v5/market/tickers?instType=SPOT"
        response = requests.get(base_url + all_tickers_url)
        if response.status_code == 200:
            data = response.json()
            if self.__min_trading_volume != None:
                symbols = [ticker['instId'] for ticker in data['data'] if ticker['instId'].endswith('USDT')
                            and not ticker['instId'].endswith(('2S-USDT', '2L-USDT', '3S-USDT', '3L-USDT', '5S-USDT', '5L-USDT'))
                            and float(ticker['volCcy24h']) > self.__min_trading_volume]
            
            else:
                symbols = [ticker['instId'] for ticker in data['data'] if ticker['instId'].endswith('USDT')
                            and not ticker['instId'].endswith(('2S-USDT', '2L-USDT', '3S-USDT', '3L-USDT', '5S-USDT', '5L-USDT'))]
                
            return symbols
        
        else:
            print("Error when getting list of Kucoin exchange tickers:", response.status_code)


    async def __okx_ws(self, ws, symbols):
        msg = {
            "op": "subscribe",
                "args": [{"channel": "tickers", "instId": symbols}]
        }

        msg = json.dumps(msg)
        await ws.send(msg)

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                print(data)
      
            except Exception as e:
                print('exp')
                

    async def __connect_to_okx_ws(self, symbols):
        async with websockets.connect(f"wss://ws.okx.com:8443/ws/v5/public") as ws:
            await self.__okx_ws(ws, symbols)


    def start_connection(self):
        symbols = self.__get_all_tickers()
        loop = asyncio.get_event_loop()
        tasks = [self.__connect_to_okx_ws(symbol) for symbol in symbols]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    



# ws = TickersOKXWebsocket(api_keys.min_trading_volume)
# ws.start_connection()

# while True:
#     time.sleep(4)
#     print(ws.ticker_list_kucoin, len(ws.ticker_list_kucoin))
#     print('\n')
#     print(len(ws.ticker_list_kucoin))


