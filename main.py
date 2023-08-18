from TikersBinanceStream import TikersBinanceWebsocket
from TikersBybitStream import TikersBybitWebsocket
from TikersKucoinStream import TickersKucoinWebsocket
from TikersMexcStream import TikersMexcWebsocket
import api_keys
import time
import pandas as pd
import numpy as np
import threading

BTC_PRICE = None

tiker_ws_binance = TikersBinanceWebsocket(api_keys.API_KEY_BINANCE, api_keys.API_SECRET_BINANCE)
tiker_ws_binance.miniTicker_arr_start()

tiker_ws_bybit = TikersBybitWebsocket(api_keys.API_KEY_BIT, api_keys.API_SECRET_BIT, api_keys.min_trading_volume)
tiker_ws_bybit.ticker_stream_start()

tiker_ws_kucoin = TickersKucoinWebsocket(api_keys.min_trading_volume)
tiker_ws_kucoin.ticker_stream_start()

tiker_ws_mexc = TikersMexcWebsocket(api_keys.min_trading_volume)
tiker_ws_mexc.ticker_stream_start()



binance_prices = tiker_ws_binance.tiker_list
baybit_prices = tiker_ws_bybit.tiker_list_bit
kucoin_prices = tiker_ws_kucoin.ticker_list_kucoin
mexc_prices = tiker_ws_mexc.tiker_list_mexc

finally_dict = {}

def min_max(row):
    # Фильтруем значения больше нуля
    filtered_values = row[row > 0]
    # Проверяем, есть ли два или более значения
    if len(filtered_values) >= 2:
        min_value = np.min(filtered_values)
        max_value = np.max(filtered_values)
        min_column = row[row == min_value].index[0]
        max_column = row[row == max_value].index[0]
        delta_percent = round(((max_value - min_value) / max_value) * 100, 2)
        if delta_percent >= 1 and delta_percent <= 10:
            finally_dict[row.name] = {
                'Spred' : delta_percent, 
                'buy_exchange' : {'exchange' : min_column, 'price' : min_value},
                'sell_exchange' : {'exchange' : max_column, 'price' : max_value}
                }
            
            print(f"{row.name}: Spred = {delta_percent}  /// {min_column} = {min_value} ---> {max_column} = {max_value}")
        return {'min': {'value': min_value, 'row': row.name, 'column': min_column},
                'max': {'value': max_value, 'row': row.name, 'column': max_column}}
    else:
        return np.nan

def create_finally_dict():
    while True:
        all_tickers = list(set(binance_prices.keys()).union(baybit_prices.keys()).union(kucoin_prices.keys()).union(mexc_prices.keys()))

        df = pd.DataFrame(index=all_tickers)
        df['binance'] = [binance_prices.get(ticker) for ticker in all_tickers]
        df['baybit'] = [baybit_prices.get(ticker) for ticker in all_tickers]
        df['kucoin'] = [kucoin_prices.get(ticker) for ticker in all_tickers]
        df['mexc'] = [mexc_prices.get(ticker) for ticker in all_tickers]


        # df = pd.DataFrame(index=set(binance_prices.keys()).union(baybit_prices.keys()).union(kucoin_prices.keys()).union(mexc_prices.keys()))
        # df['binance'] = [binance_prices.get(ticker) for ticker in df.index]
        # df['baybit'] = [baybit_prices.get(ticker) for ticker in df.index]
        # df['kucoin'] = [kucoin_prices.get(ticker) for ticker in df.index]
        # df['mexc'] = [mexc_prices.get(ticker) for ticker in df.index]

        df.fillna(value=0, inplace=True)

        # Применяем функцию к каждой строке
        df['min_max_values'] = df.apply(min_max, axis=1)

        # print(finally_dict)
        try:
            BTC_PRICE = {
                'Binance' : df['binance']['BTCUSDT'],
                'Baybit' : df['baybit']['BTCUSDT'],
                'Kucoin' : df['kucoin']['BTCUSDT'],
                'Mexc' : df['mexc']['BTCUSDT']
            }

            print(f"\nBTCUSDT: Binance = ${BTC_PRICE['Binance']}, Baybit = ${BTC_PRICE['Baybit']}, Kucoin = ${BTC_PRICE['Kucoin']}, Mexc = ${BTC_PRICE['Mexc']}")
            # print('\n')

        except:
            # print("except : BTC_PRICE = None!")
            BTC_PRICE = None
        time.sleep(5)

# threading.Thread(target=create_finally_dict, daemon=True).start()
create_finally_dict()
