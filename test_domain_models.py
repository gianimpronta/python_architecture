import unittest
from model import Product, Batch, OrderLine, allocate, Customer
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)


class DomainModelTest(unittest.TestCase):

    @staticmethod
    def make_product_batch_order_line(sku, product_name, batch_ref,
                                      batch_qty, order_id, order_qty):
        product: Product = Product(sku, product_name)
        batch = Batch(batch_ref, product, batch_qty)
        order_line = OrderLine(order_id, product.sku, order_qty)
        return product, batch, order_line

    def test_order_alocation_calculation(self):
        product, batch, order_line = self.make_product_batch_order_line(
            sku=1,
            product_name='small-table',
            batch_ref=1,
            batch_qty=20,
            order_qty=2,
            order_id=3
        )
        batch.allocate(order_line)
        self.assertEqual(18, batch.available_quantity)

    def test_cant_sell_more_than_stock_available(self):
        product, batch, order_line = self.make_product_batch_order_line(
            sku=2,
            product_name='blue-cushion',
            batch_ref=2,
            batch_qty=1,
            order_qty=2,
            order_id=4
        )
        batch.allocate(order_line)
        self.assertEqual(batch._available_quantity, 1)

    def test_allocate_same_line_twice(self):
        product, batch, order_line = self.make_product_batch_order_line(
            sku=3,
            product_name='blue-vase',
            batch_ref=3,
            batch_qty=10,
            order_qty=2,
            order_id=2
        )
        batch.allocate(order_line)
        batch.allocate(order_line)
        self.assertEqual(8, batch.available_quantity)

    def test_cannot_allocate_different_sku(self):
        product = Product('4', 'White-glass')
        product2 = Product('5', 'Blue-glass')
        batch = Batch(4, product2, 10)
        order_line = OrderLine(1, product.sku, 1)
        batch.allocate(order_line)
        self.assertEqual(batch._available_quantity, 10)

    def test_can_only_deallocate_allocated_lines(self):
        product, batch, deallocate_line = self.make_product_batch_order_line(
            sku=4,
            product_name='white-vase',
            batch_ref=5,
            batch_qty=10,
            order_qty=2,
            order_id=1
        )
        batch.deallocate(deallocate_line)
        self.assertEqual(batch._available_quantity, 10)

    def test_deallocate_allocated_lines(self):
        product, batch, order_line = self.make_product_batch_order_line(
            sku=4,
            product_name='white-vase',
            batch_ref=5,
            batch_qty=10,
            order_qty=2,
            order_id=2
        )
        batch.allocate(order_line=order_line)
        batch.deallocate(order_line)
        self.assertEqual(10, batch._available_quantity)

    def test_prefers_current_stock_to_shipments(self):
        product = Product('1', 'clocks')
        in_stock = Batch('In-stock', product, 100, None)
        shipment = Batch('shipment', product, 100, tomorrow)
        order_line = OrderLine(1, '1', 10)
        allocate(order_line, [in_stock, shipment])

        self.assertEqual(90, in_stock.available_quantity)
        self.assertEqual(100, shipment.available_quantity)

    def test_prefer_earlier_batches(self):
        product = Product('2', 'spoon')
        earliest = Batch('earliest', product, 100, today)
        medium = Batch('medium', product, 100, tomorrow)
        latest = Batch('latest', product, 100, later)
        order_line = OrderLine(1, '2', 10)
        allocate(order_line, [earliest, medium, latest])

        self.assertEqual(90, earliest.available_quantity)
        self.assertEqual(100, medium.available_quantity)
        self.assertEqual(100, latest.available_quantity)

    def test_returns_allocated_batch_ref(self):
        product = Product('3', 'cups')
        in_stock = Batch('In-stock', product, 100, None)
        shipment = Batch('shipment', product, 100, tomorrow)
        order_line = OrderLine(1, '3', 10)
        allocation = allocate(order_line, [in_stock, shipment])
        self.assertEqual(in_stock.reference, allocation)

    def test_customer_eq_methods(self):
        c1 = Customer('John')
        c2 = Customer('John')
        c3 = Customer('Jane')
        p1 = Product('101', 'Cardholder')

        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertNotEqual(c1, p1)

    def test_product_eq_method(self):
        p1 = Product('101', 'Cardholder')
        p2 = Product('102', 'Poker chips')
        p3 = Product('101', 'Deck of cards')
        c1 = Customer('John')

        self.assertEqual(p1, p3)
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p3, p2)
        self.assertNotEqual(p1, c1)

    def test_purchasebatch_eta(self):
        p1 = Product('101', 'Cardholder')
        batch = Batch('1', p1, 100)
        batch2 = Batch('2', p1, 100, today)

        self.assertGreater(batch2, batch)

    def test_purchasebatch_eq(self):
        p1 = Product('101', 'Cardholder')
        batch = Batch('1', p1, 100)
        batch2 = Batch('2', p1, 100, today)
        batch3 = Batch('1', p1, 100)

        self.assertNotEqual(batch, batch2)
        self.assertNotEqual(batch3, batch2)
        self.assertEqual(batch, batch3)


if __name__ == '__main__':
    unittest.main()
