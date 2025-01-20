import backtrader as bt
import itertools

from back_trader.fetch_data_for_bt import get_data_from_yahoo
from back_trader.strategy.buy_and_hold import BuyAndHold
from back_trader.strategy.vix import vixCross
from src.utilities.simulation_config import initial_cash, commission, start_date, end_date
from src.utilities.manage_txt_file import delete_file_if_exists, write_dict_to_file


def backtrader_with_strategy(data_feed, strategy, cerebro_plot=True, strategy_params=None):
    """
    Run backtrader with a strategy.

    :parameter:
    - data_feed: DataFrame, stock price data
    - strategy: class, strategy class
    - cerebro_plot: bool, optional, plot the graph
    - strategy_params: dict, optional, strategy parameters

    :return:
    - total_return: float, total return rate
    """
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)

    if strategy_params is None:
        cerebro.addstrategy(strategy)
    else:
        cerebro.addstrategy(strategy, strategy_params)

    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addsizer(bt.sizers.AllInSizer)

    # Set initial cash
    cerebro.broker.setcash(initial_cash)

    # Set commission
    cerebro.broker.setcommission(commission=commission, margin=1)

    # Analyzer
    # cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual_return')
    # cerebro.addanalyzer(btanalyzers.PyFolio, _name='pyfolio')
    # cerebro.addanalyzer(btanalyzers.PeriodStats, _name='period_stats')
    # cerebro.addanalyzer(btanalyzers.Returns, _name='returns', tann=252)
    # cerebro.addanalyzer(btanalyzers.TimeReturn, _name='time_return')

    thestrats = cerebro.run()

    # thestrat = thestrats[0]
    # annual_return = thestrat.analyzers.annual_return.get_analysis()
    # pyfolio = thestrat.analyzers.pyfolio.get_analysis()
    # period_stats = thestrat.analyzers.period_stats.get_analysis()
    # returns = thestrat.analyzers.returns.get_analysis()
    # time_return = thestrat.analyzers.time_return.get_analysis()

    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_cash) / initial_cash * 100
    print("total return rate = " + str(round(total_return, 3)) + "%")

    if cerebro_plot:
        cerebro.plot()

    return total_return


def best_params_calc(buy_and_hold_total_ret):
    """
    Calculate the best parameters for the strategy.

    :parameter:
    - buy_and_hold_total_ret: float, buy and hold total return rate
    """
    file_path = "./best_params.txt"
    file_path2 = "./greater_than_buy_and_hold_params.txt"
    delete_file_if_exists(file_path)
    delete_file_if_exists(file_path2)
    best_params = {'rolling_days': 1, 'vix_th': 1, 'total_return': 0}
    write_dict_to_file(file_path, 'buy_and_hold_total_return = ' + str(buy_and_hold_total_ret), header="")
    write_dict_to_file(file_path2, 'buy_and_hold_total_return = ' + str(buy_and_hold_total_ret), header="")
    counter = 0
    for rolling_days, vix_th in itertools.product(range(1, 2), range(1, 101, 1)):
        counter += 1
        params = {'rolling_days': rolling_days, 'vix_th': vix_th}
        total_return = backtrader_with_strategy(data_feed, vixCross, cerebro_plot=False, strategy_params=params)
        if total_return > best_params['total_return']:
            best_params = {'rolling_days': rolling_days, 'vix_th': vix_th, 'total_return': total_return}
            print(best_params)
            write_dict_to_file(file_path, best_params, header="")
        if total_return > buy_and_hold_total_ret:
            better_than_buy_and_hold_params = {'rolling_days': rolling_days, 'vix_th': vix_th,
                                               'total_return': total_return}
            print(f'better_than_buy_and_hold_params')
            write_dict_to_file(file_path2, better_than_buy_and_hold_params, header="")

    print(counter)
    print(best_params)


if __name__ == '__main__':
    ticker = 'SPY'
    data_feed = get_data_from_yahoo(ticker, start_date, end_date)
    buy_and_hold_total_return = backtrader_with_strategy(data_feed, BuyAndHold)

    # params = {'rolling_days': 1, 'vix_th': 51}  # COVID-19 and the march 2020 stock market crash
    # backtrader_with_strategy(data_feed, vixCross, strategy_params=params)

    best_params_calc(buy_and_hold_total_return)
