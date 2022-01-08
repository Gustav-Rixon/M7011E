from Lorax import Buffert, Prosumer


class Market:
    def __init__(self, market_size):
        # The market is empty when started
        self.market_buffert = Buffert(market_size, 0)
        self.market_price = 100  # Starting market price

    # CAN BE pos and neg
    def update_market(self, amount):
        self.market_buffert.content += amount
        Buffert.buffert_checker(self.market_buffert)

        if self.market_buffert.content <= 0:
            self.market_buffert.content = 0

    # ONLY POS
    def send_to_market(self, amount):
        self.market_buffert.content += amount

    # ONLY NEG
    def buy_from_market(self, amount):
        self.market_buffert.content -= amount

    def change_market_size(self, amount):
        self.market_buffert.capacity = amount

    # y = kx+m, k = number of users, x = current consumtion, m = fast pris öre/kWh

    def calculate_electricity_price(self, current_consumption, number_of_users, fixed_price):
        if ((number_of_users*current_consumption) + fixed_price - self.market_buffert.content <= fixed_price):
            self.market_price = fixed_price
        else:
            self.market_price = (
                number_of_users*current_consumption) + fixed_price - self.market_buffert.content
