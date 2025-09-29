"""Price value object."""
# Standard Python Libraries
from decimal import Decimal
from typing import Union


class Price:
    """Price value object representing monetary amounts."""

    def __init__(self, amount: Union[Decimal, float, int, str]):
        """Initialize Price value object.

        Args:
            amount: Price amount as Decimal, float, int, or string
        """
        if isinstance(amount, str):
            amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))

        if amount < 0:
            raise ValueError("Price cannot be negative")

        self._amount = amount

    @property
    def amount(self) -> Decimal:
        """Get the price amount."""
        return self._amount

    def __str__(self) -> str:
        """Return string representation of Price."""
        return f"${self._amount}"

    def __repr__(self) -> str:
        """Return detailed string representation of Price."""
        return f"Price({self._amount})"

    def __eq__(self, other) -> bool:
        """Check equality based on amount."""
        if not isinstance(other, Price):
            return False
        return self._amount == other._amount

    def __lt__(self, other) -> bool:
        """Check if this price is less than other."""
        if not isinstance(other, Price):
            return NotImplemented
        return self._amount < other._amount

    def __le__(self, other) -> bool:
        """Check if this price is less than or equal to other."""
        if not isinstance(other, Price):
            return NotImplemented
        return self._amount <= other._amount

    def __gt__(self, other) -> bool:
        """Check if this price is greater than other."""
        if not isinstance(other, Price):
            return NotImplemented
        return self._amount > other._amount

    def __ge__(self, other) -> bool:
        """Check if this price is greater than or equal to other."""
        if not isinstance(other, Price):
            return NotImplemented
        return self._amount >= other._amount

    def __add__(self, other) -> "Price":
        """Add two prices."""
        if not isinstance(other, Price):
            return NotImplemented
        return Price(self._amount + other._amount)

    def __sub__(self, other) -> "Price":
        """Subtract two prices."""
        if not isinstance(other, Price):
            return NotImplemented
        return Price(self._amount - other._amount)

    def __mul__(self, other) -> "Price":
        """Multiply price by a number."""
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        return Price(self._amount * Decimal(str(other)))

    def __truediv__(self, other) -> "Price":
        """Divide price by a number."""
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        return Price(self._amount / Decimal(str(other)))

    def calculate_discount_percentage(self, original_price: "Price") -> Decimal:
        """Calculate discount percentage compared to original price."""
        if original_price._amount == 0:
            return Decimal("0")
        return ((original_price._amount - self._amount) / original_price._amount) * 100
