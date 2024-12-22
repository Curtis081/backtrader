import backtrader as bt
import numpy as np
import pandas as pd

from back_trader.fetch_data_for_bt import fetch_data_from_yahoo, convert_to_backtrader_data_format
from back_trader.strategy.common_strategy import commonStrategy
from simulation_setting import start_date, end_date


def get_vix(start_date, end_date):
    # start_date = self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d')
    # end_date = self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d')

    vix_symbol = "^VIX"
    vix_data = fetch_data_from_yahoo(vix_symbol, start_date, end_date)

    # vix_data.to_csv("vix_historical_data.csv")

    return vix_data


def vix_indicator(df, rolling_days, vix_th):
    shift_days = 1
    df['previous_trading_day_close_price'] = df['Close'].shift(shift_days)

    last_value = df['previous_trading_day_close_price'].iloc[shift_days]
    df['price_filled_last_value'] = df['previous_trading_day_close_price'].fillna(last_value)
    df['price_sma'] = (
        df['price_filled_last_value'].rolling(rolling_days).mean())

    df['hold_flat_signal'] = np.where(df['price_sma'] > vix_th, -1,
                                      np.where(df['price_sma'] <= vix_th, 1, 1))
    # Greater than vix_th, set -1 (flat, close position), otherwise set 1 (hold, hold position)

    df['buy'] = (df['hold_flat_signal'] == 1) & (df['hold_flat_signal'].shift(1) == -1)
    df['sell'] = (df['hold_flat_signal'] == -1) & (df['hold_flat_signal'].shift(1) == 1)
    df['buy_sell_signal'] = np.where(df['buy'], 1, np.where(df['sell'], -1, 0))

    # df['indicator'] = df['hold_flat_signal']
    df['indicator'] = df['buy_sell_signal']
    indicator = df[['indicator']].copy()
    return indicator


class FixedLine(bt.Indicator):
    lines = ('fixed',)

    def __init__(self, value):
        self.value = value

    def next(self):
        self.lines.fixed[0] = self.value


def counter():
    counter = 0
    while True:
        yield counter
        counter = counter + 1


class vixCross(commonStrategy):
    def __init__(self, strategy_params):
        super().__init__()
        vix = get_vix(start_date, end_date)
        rolling_days = strategy_params['rolling_days']
        vix_th = strategy_params['vix_th']
        self.indicator = vix_indicator(vix, rolling_days=rolling_days, vix_th=vix_th)
        self.next_counter = counter()

    def next(self):
        next_num = next(self.next_counter)
        if next_num == 0:
            size = self.buy_all_the_available_cash()
            self.buy(size=size)
            return

        # For debug
        # time_stamp_now = self.indicator.index[next_num]
        # if time_stamp_now == pd.Timestamp('2008-12-18 00:00:00'):
        #     print()

        buy_sell_signal = self.indicator.iloc[next_num]['indicator']
        if not self.position:
            if buy_sell_signal > 0:
                size = self.buy_all_the_available_cash()
                self.buy(size=size, checksubmit=False)  # do not check submit to ignore Margin(T+2) problem
        else:
            if buy_sell_signal < 0:
                self.close()
