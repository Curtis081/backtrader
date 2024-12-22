import backtrader as bt
import backtrader.analyzers as btanalyzers
import itertools
import os

from back_trader.fetch_data_for_bt import get_data_from_yahoo
from back_trader.strategy.buy_and_hold import BuyAndHold
from back_trader.strategy.sma import SmaCross
from back_trader.strategy.vix import vixCross
from simulation_setting import initial_cash, commission, start_date, end_date


def backtrader_with_strategy(data_feed, strategy, strategy_params=None):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)

    if strategy_params is None:
        cerebro.addstrategy(strategy)
    else:
        cerebro.addstrategy(strategy, strategy_params)

    # 添加 Broker 觀察者
    # cerebro.addobserver(bt.observers.Broker)
    #
    # # 添加 BuySell 觀察者，標記交易點
    # cerebro.addobserver(bt.observers.BuySell)

    # cerebro.addsizer(bt.sizers.AllInSizer)

    # Set initial cash
    cerebro.broker.setcash(initial_cash)

    # Set commission
    cerebro.broker.setcommission(commission=commission, margin=1)

    # Analyzer
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual_return')
    cerebro.addanalyzer(btanalyzers.PyFolio, _name='pyfolio')
    cerebro.addanalyzer(btanalyzers.PeriodStats, _name='period_stats')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns', tann=252)
    cerebro.addanalyzer(btanalyzers.TimeReturn, _name='time_return')

    thestrats = cerebro.run()
    thestrat = thestrats[0]
    annual_return = thestrat.analyzers.annual_return.get_analysis()
    pyfolio = thestrat.analyzers.pyfolio.get_analysis()
    period_stats = thestrat.analyzers.period_stats.get_analysis()
    returns = thestrat.analyzers.returns.get_analysis()
    time_return = thestrat.analyzers.time_return.get_analysis()

    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_cash) / initial_cash * 100
    print(total_return)

    cerebro.plot()

    return total_return


def delete_file_if_exists(file_path):
    """
    If the file exists, delete the file.

    :param file_path: str, target file path
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"file {file_path} deleted")
    else:
        print(f"file {file_path} does not exist, no need to delete")


def write_dict_to_file(file_path, data, header=None):
    """
    Write a dictionary to a file. If the file does not exist, add a header.

    :param file_path: str, target file path
    :param data: dict, need to write dictionary
    :param header: str, optional, file header(only write when file does not exist)
    """
    file_exists = os.path.exists(file_path)

    with open(file_path, "a") as file:
        if not file_exists and header:
            file.write(header + "\n")
            file.write("-" * len(header) + "\n")

        file.write(f"\n")
        for key, value in data.items():
            file.write(f"{key}: {value}\n")

    print(f"dirctory contents written to {file_path}")


if __name__ == '__main__':
    ticker = 'SPY'
    data_feed = get_data_from_yahoo(ticker, start_date, end_date)

    backtrader_with_strategy(data_feed, BuyAndHold)

    params = {'rolling_days': 1, 'vix_th': 44}
    backtrader_with_strategy(data_feed, vixCross, strategy_params=params)

    # file_path = "best_params.txt"
    # delete_file_if_exists(file_path)
    # best_params = {'rolling_days': 1, 'vix_th': 1, 'total_return': 0}
    # for rolling_days, vix_th in itertools.product(range(1, 2), range(1, 100, 1)):
    #     params = {'rolling_days': rolling_days, 'vix_th': vix_th}
    #     total_return = backtrader_with_strategy(data_feed, vixCross, strategy_params=params)
    #     if total_return > best_params['total_return']:
    #         best_params['rolling_days'] = rolling_days
    #         best_params['vix_th'] = vix_th
    #         best_params['total_return'] = total_return
    #         print(f'rolling_days: {rolling_days}, vix_th: {vix_th}, total_return: {total_return}')
    #         write_dict_to_file(file_path, best_params, header="")
    # print(best_params)
