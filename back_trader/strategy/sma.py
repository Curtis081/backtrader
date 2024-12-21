import backtrader as bt


from back_trader.strategy.common_strategy import commonStrategy


class SmaCross(commonStrategy):
    params = (
        ('sma_short', 20),  # 短期移動平均線
        ('sma_long', 60),   # 長期移動平均線
    )

    def __init__(self):
        # 定義移動平均線
        sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_short)
        sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_long)

        # 定義買入和賣出的信號
        self.crossover = bt.indicators.CrossOver(sma_short, sma_long)

        # self.sma = bt.indicators.SimpleMovingAverage(self.data0, period=15)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # 短期均線向上穿越長期均線
                size = self.buy_all_the_available_cash()
                self.buy(size=size)
        else:
            if self.crossover < 0:  # 短期均線向下穿越長期均線
                self.close()
