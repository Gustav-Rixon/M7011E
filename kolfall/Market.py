class Market:
    def __init__(self, market_size):
        self.market_buffert = 0  # The market is empty when started
        self.market_size = market_size
        self.market_price = 100  # Starting market price

    def send_to_market(self, amount):
        self.market_buffert += amount

    def buy_from_market(self, amount):
        self.market_buffert -= amount

    # y = kx+m, k = number of users, x = current consumtion, m = fast pris öre/kWh
    def calculate_electricity_price(self, current_consumption, number_of_users, fixed_price):
        if ((number_of_users*current_consumption) + fixed_price - self.market_buffert <= fixed_price):
            self.market_price = fixed_price
        else:
            self.market_price = (
                number_of_users*current_consumption) + fixed_price - self.market_buffert
