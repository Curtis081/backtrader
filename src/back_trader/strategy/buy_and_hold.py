from src.back_trader.strategy.common_strategy import commonStrategy


class BuyAndHold(commonStrategy):
    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy all the available cash
        size = self.buy_all_the_available_cash()
        self.buy(size=size)

    # def stop(self):
    #     print(self.broker.get_value())
    #     # calculate the actual returns
    #     self.roi = (self.broker.get_value() / self.val_start) - 1.0
    #     print('ROI:        {:.2f}%'.format(100.0 * self.roi))
