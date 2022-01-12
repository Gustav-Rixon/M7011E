from Backend.Lorax import Buffert


class Market:
    """[summary]
        This module handels market transaction
    """

    def __init__(self, market_size):
        # The market is empty when started
        self.market_buffert = Buffert(market_size, 0)
        self.market_price = 100  # Starting market price in öre
        self.recommended_market_price = 0

    def update_market(self, amount):
        """[summary]

        Args:
            amount ([type]): [description]
        """
        self.market_buffert.content += amount
        Buffert.buffert_checker(self.market_buffert)

        if self.market_buffert.content <= 0:
            self.market_buffert.content = 0

    def send_to_market(self, amount):
        """[summary]
            This function sends to the market

        Args:
            amount ([int]): [amount to add to the market]
        """
        self.market_buffert.content += amount

    def buy_from_market(self, amount):
        """[summary]
            This function is called when a user buys from the market.
            The amount is removed from the market objects buffert.

        Args:
            amount ([int]): [The amount to sell]
        """
        self.market_buffert.content -= amount

    def change_market_size(self, amount):
        """[summary]
            This function changes the market size of the simulation

        Args:
            amount ([int]): [The new size of the market]
        """
        self.market_buffert.capacity = amount

    def calculate_recommended_electricity_price(self, current_consumption, number_of_users):
        """[summary]
            Calculates the recommended electricity price of the cycle.

        Args:
            current_consumption ([int]): [current consumption of the simulation]
            number_of_users ([int]): [number of users in the simulation]
        """

        # Check so that price is not less then fixed price
        self.recommended_market_price = (
            number_of_users*current_consumption) - self.market_buffert.content
