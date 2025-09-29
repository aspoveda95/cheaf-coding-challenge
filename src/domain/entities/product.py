"""Product domain entity."""
# Standard Python Libraries
from typing import Optional
from uuid import UUID, uuid4

# Local Libraries
from src.domain.value_objects.price import Price


class Product:
    """Product entity representing a marketplace item."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = "",
        description: str = "",
        original_price: Optional[Price] = None,
        is_active: bool = True,
        stock_quantity: int = 0,
    ):
        """Initialize Product entity.

        Args:
            id: Unique identifier for the product
            name: Product name
            description: Product description
            original_price: Original price of the product
            is_active: Whether the product is active
            stock_quantity: Available stock quantity
        """
        self._id = id or uuid4()
        self._name = name
        self._description = description
        self._original_price = original_price
        self._is_active = is_active
        self._stock_quantity = stock_quantity

    @property
    def id(self) -> UUID:
        """Get the product ID."""
        return self._id

    @property
    def name(self) -> str:
        """Get the product name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the product description."""
        return self._description

    @property
    def original_price(self) -> Optional[Price]:
        """Get the original price."""
        return self._original_price

    @property
    def is_active(self) -> bool:
        """Check if the product is active."""
        return self._is_active

    @property
    def stock_quantity(self) -> int:
        """Get the stock quantity."""
        return self._stock_quantity

    def activate(self) -> None:
        """Activate the product."""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate the product."""
        self._is_active = False

    def update_price(self, price: Price) -> None:
        """Update product price."""
        self._original_price = price

    def update_stock(self, quantity: int) -> None:
        """Update stock quantity."""
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        self._stock_quantity = quantity

    def reduce_stock(self, quantity: int) -> None:
        """Reduce stock quantity."""
        if quantity < 0:
            raise ValueError("Quantity to reduce cannot be negative")
        if self._stock_quantity < quantity:
            raise ValueError("Insufficient stock")
        self._stock_quantity -= quantity

    def add_stock(self, quantity: int) -> None:
        """Add stock quantity."""
        if quantity < 0:
            raise ValueError("Quantity to add cannot be negative")
        self._stock_quantity += quantity

    def is_available(self) -> bool:
        """Check if product is available (active and in stock)."""
        return self._is_active and self._stock_quantity > 0

    def __str__(self) -> str:
        """Return string representation of Product."""
        return f"Product({self._name})"

    def __repr__(self) -> str:
        """Return detailed string representation of Product."""
        return f"Product(id={self._id}, name={self._name})"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Product):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self._id)
