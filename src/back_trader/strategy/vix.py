import numpy as np

from src.back_trader.fetch_data_for_bt import fetch_data_from_yahoo
from src.back_trader.strategy.common_strategy import commonStrategy
from src.utilities.simulation_config import start_date, end_date


def get_vix_history_data(_start_date, _end_date):
    """
    The get_vix_history_data function fetches the historical data for the VIX index.

    :Parameters:
    start_date: The start date for the historical data.
    end_date: The end date for the historical data.

    :return:
    vix_data: The DataFrame containing the historical data for the VIX index.
    """
    vix_symbol = "^VIX"
    vix_data = fetch_data_from_yahoo(vix_symbol, _start_date, _end_date)
    return vix_data


def vix_hold_flat_indicator(df, rolling_days, vix_th):
    """
    The vix_hold_flat_indicator function calculates the VIX hold/flat indicator.

    :Parameters:
    df: The DataFrame containing the VIX data.
    rolling_days: The number of days to use for the rolling average of the VIX.
    vix_th: The threshold value for the VIX.

    :return:
    indicator: The DataFrame containing the VIX hold/flat indicator.

    """
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


def counter():
    """
    The counter is used to count the number of days since the start of the strategy.
    It is a generator that yields the next number each time it is called.
    """
    counter_reg = 0
    while True:
        yield counter_reg
        counter_reg = counter_reg + 1



class vixCross(commonStrategy):
    """
        The vixCross class is a subclass of the commonStrategy class.
        It is used to implement the VIX cross strategy.
        The strategy is to buy when the VIX crosses below a threshold and sell when the VIX crosses above the threshold.

        :Parameters:
        strategy_params: A dictionary containing the rolling_days and vix_th parameters, as follows:
        vix_th: The threshold value for the VIX.
        rolling_days: The number of days to use for the rolling average of the VIX.

        :return: None
    """
    def __init__(self, strategy_params):
        super().__init__()
        vix = get_vix_history_data(start_date, end_date)
        rolling_days = strategy_params['rolling_days']
        vix_th = strategy_params['vix_th']
        self.indicator = vix_hold_flat_indicator(vix, rolling_days=rolling_days, vix_th=vix_th)
        self.next_counter = counter()

    def next(self):
        next_num = next(self.next_counter)
        if next_num == 0:
            size = self.buy_all_the_available_cash()
            self.buy(size=size)
            return

        # # For debug purpose only
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
