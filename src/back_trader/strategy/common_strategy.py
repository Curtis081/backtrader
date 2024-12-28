import backtrader as bt
from src.simulation_setting import commission, do_log_print


class commonStrategy(bt.Strategy):
    """
    The commonStrategy class is for other strategies to inherit from.
    It contains the common methods and attributes that are used in the strategies.
    """
    def __init__(self):
        pass

    def buy_all_the_available_cash(self):
        size = int(self.broker.get_cash() / (self.data * (1 + commission)))
        return size

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            order_status = order.getstatusname()
            self.log('Order: %s' % order_status)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f\n' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None, doPrint=do_log_print):
        if doPrint:
            dt = dt or self.data.datetime[0]
            dt_str = bt.num2date(dt).strftime('%Y-%m-%d %H:%M:%S')
            print('%s, %s' % (dt_str, txt))

    # def stop(self):
    #     print(self.broker.get_value())
