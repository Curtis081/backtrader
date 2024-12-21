import backtrader as bt


from back_trader.fetch_data_for_bt import GetDataFromYahoo
from back_trader.strategy.buy_and_hold import BuyAndHold
from back_trader.strategy.sma import SmaCross
from back_trader.strategy.vix import vixCross
from public import commission


def backtrader_with_strategy(data_feed, strategy):
    # 創建一個 Cerebro 引擎
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.adddata(vix, name='VIX')

    # 添加策略
    cerebro.addstrategy(strategy)

    # # 添加 Broker 觀察者
    # cerebro.addobserver(bt.observers.Broker)
    #
    # # 添加 BuySell 觀察者，標記交易點
    # cerebro.addobserver(bt.observers.BuySell)

    # cerebro.addsizer(bt.sizers.AllInSizer)

    # 設定初始現金
    cerebro.broker.setcash(100000.0)

    # 設定每次交易的手續費
    cerebro.broker.setcommission(commission=commission)

    result = cerebro.run()

    # 繪製結果
    cerebro.plot()


def get_vix(start_date, end_date):
    # start_date = self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d')
    # end_date = self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d')

    # 定義 VIX 指數的代碼
    vix_symbol = "^VIX"
    # 下載 VIX 歷史數據
    vix_data = GetDataFromYahoo(vix_symbol, start_date, end_date)

    # 將數據保存為 CSV 檔案
    # vix_data.to_csv("vix_historical_data.csv")

    return vix_data


if __name__ == '__main__':
    ticker = 'SPY'
    start_date = '1993-02-01'
    end_date = '2020-12-01'

    data_feed = GetDataFromYahoo(ticker, start_date, end_date)
    vix = get_vix(start_date, end_date)

    backtrader_with_strategy(data_feed, BuyAndHold)
    backtrader_with_strategy(data_feed, vixCross)
