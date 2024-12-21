import backtrader as bt


from back_trader.strategy.common_strategy import commonStrategy


class FixedLine(bt.Indicator):
    lines = ('fixed',)

    def __init__(self, value):
        self.value = value

    def next(self):
        self.lines.fixed[0] = self.value


class vixCross(commonStrategy):
    params = (('vix_th', 50),)
    def __init__(self):
        self.first_next = True
        # 確保 VIX 是 Backtrader 數據流
        self.vix = self.getdatabyname("VIX")
        self.vix_close = self.vix.close

        self.fixed_line = FixedLine(value=self.params.vix_th)

        vix_sma = bt.indicators.SimpleMovingAverage(self.vix.close, period=5)
        self.over_threshold = self.vix.close - self.fixed_line

    def next(self):
        if self.first_next:
            self.first_next = False
            size = self.buy_all_the_available_cash()
            self.buy(size=size)
            return

        if not self.position:
            if self.over_threshold < 0:
                size = self.buy_all_the_available_cash()
                self.buy(size=size)
        else:
            if self.over_threshold > 0:
                self.close()
