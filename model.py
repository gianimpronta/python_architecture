from dataclasses import dataclass
from typing import List


@dataclass
class Customer:
    name: str


@dataclass
class Product:
    sku: str
    name: str

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.sku == other.sku


@dataclass(frozen=True)
class OrderLine:
    orderid: int
    sku: str
    quantity: int


class Batch:

    def __init__(self, ref, product, qty, eta=None):
        self.reference = ref
        self.sku = product.sku
        self._initial_quantity = qty
        self._available_quantity = self._initial_quantity
        self._order_lines = set()
        self.eta = eta

    def allocate(self, order_line):
        if self.can_allocate(order_line):
            self._order_lines.add(order_line)

    def can_allocate(self, order_line):
        if order_line.quantity > self._available_quantity:
            return False
        if self.sku != order_line.sku:
            return False
        return True

    def deallocate(self, line):
        if line in self._order_lines:
            self._order_lines.remove(line)

    @property
    def available_quantity(self):
        return self._initial_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        return sum([o.quantity for o in self._order_lines])

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return self.reference

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return other.eta < self.eta


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    batch = next(b for b in sorted(batches) if b.can_allocate(line))
    batch.allocate(line)
    return batch.reference
