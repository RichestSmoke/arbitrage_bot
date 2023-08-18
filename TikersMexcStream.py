import requests
import certifi, os
import time
import websockets
import threading
import asyncio
import json
import traceback


class TikersMexcWebsocket:
    def __init__(self, min_trading_volume: float = None) -> None:
        os.environ['SSL_CERT_FILE'] = certifi.where()
        self.tiker_list_mexc = {} 
        self.threads = []
        self.__min_trading_volume = min_trading_volume


    def __get_symbol(self):
        base_endpoint = 'https://api.mexc.com'
        default_symbols_endpoint = '/api/v3/ticker/24hr'
        response = requests.get(base_endpoint + default_symbols_endpoint)
        if response.status_code == 200:
            symbols = response.json()
            if self.__min_trading_volume != None:
                symbols = [ticker['symbol'] for ticker in symbols if ticker['symbol'].endswith('USDT')
                            and not ticker['symbol'].endswith(('2SUSDT', '2LUSDT', '3SUSDT', '3LUSDT', '5SUSDT', '5LUSDT'))
                            and float(ticker['lastPrice']) * float(ticker['volume']) > self.__min_trading_volume]
            else:
                symbols = [ticker['symbol'] for ticker in symbols if ticker['symbol'].endswith('USDT')
                            and not ticker['symbol'].endswith(('2SUSDT', '2LUSDT', '3SUSDT', '3LUSDT', '5SUSDT', '5LUSDT'))]
            
            symbols_lists = [symbols[i:i+25] for i in range(0, len(symbols), 25)]
            return symbols_lists
        
        else:
            print("Ошибка при получении списка тикеров биржи Mexc:", response.status_code)


    async def __send_ping(self, ws):
        while self.running:
            await asyncio.sleep(30)
            params = {"method": "ping"}
            await ws.send(json.dumps(params))


    async def __mexcws(self, symbol_list):
        async with websockets.connect("wss://wbs.mexc.com/ws") as ws:
            params = {
                "method": "SUBSCRIPTION",
                "params":["spot@public.deals.v3.api@" + symbol for symbol in symbol_list]
                }
            await ws.send(json.dumps(params))
            asyncio.create_task(self.__send_ping(ws))

            # Stay alive forever, listening to incoming msgs
            while self.running:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    symbol = data['s']
                    price = float(data['d']['deals'][0]['p'])
                    # print(symbol, ' = ', price)
                    self.tiker_list_mexc[symbol] = price
                    
                except traceback and Exception as e:
                    # print(f"[Mexc]Error processing message: {e}")
                    traceback.print_exception
                    pass
                            
    
    def __start_connection(self, symbol_list):
        # Start the connection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__mexcws(symbol_list))
    
    
    def ticker_stream_start(self):
        self.running = True
        symbol_lists = self.__get_symbol()
        for symbol_list in symbol_lists:
            thread = threading.Thread(target=self.__start_connection, args=(symbol_list,), daemon=True).start()
            self.threads.append(thread)  # Добавляем созданный поток в список

    def stop_ticker_stream(self):
        self.running = False
        for thread in self.threads:
            print(f'Поток {thread} завершился') # Ожидаем завершения каждого потока
            thread.join() 


# import api_keys
# a = TikersMexcWebsocket(api_keys.min_trading_volume)
# a.ticker_stream_start()

# while True:
#     try:
#         time.sleep(3)
#         print(a.tiker_list_mexc, len(a.tiker_list_mexc))

#     except KeyboardInterrupt:
#         print('exp')
#         break
     
