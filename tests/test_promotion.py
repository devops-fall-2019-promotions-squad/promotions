"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
from mongoengine import connect
from service import app
from service.models import Promotion, Product
from .promotion_factory import PromotionFactory

######################################################################
#  T E S T   C A S E S
######################################################################

class TestPromotion(unittest.TestCase):
    """ Test cases for Promotions """

    @classmethod
    def setUpClass(cls):
        """ Run once before all test cases """
        app.debug = False

    @classmethod
    def tearDownClass(cls):
        """ Run once after all test cases """
        pass

    def setUp(self):
        """ Runs before each test """
        db = connect('promotion')
        db.drop_database('promotion')  # clean up the last tests

    def tearDown(self):
        """ Runs after each test """
        db = connect('promotion')
        db.drop_database('promotion')  # clean up the last tests

    def test_find_by_code(self):
        """ Find Promotions by code """
        self.assertEqual(len(Promotion.all()), 0)
        codes = ['SAVE15', 'SAVE20', 'SAVE30']
        counts = [10, 15, 2]
        for count, code in zip(counts, codes):
            for _ in range(count):
                promotion = PromotionFactory()
                promotion.code = code
                promotion.save()

        for count, code in zip(counts, codes):
            promotions = Promotion.find_by_code(code)
            self.assertEqual(len(promotions), count)
            for promotion in promotions:
                self.assertEqual(promotion.code, code)

    def test_find(self):
        """ Find a Promotion by ID """
        Promotion(code='SAVE30',
                  percentage=70,
                  start_date='2019-10-01',
                  expiry_date='2019-11-01').save()
        save50 = Promotion(code="SAVE50",
                           percentage=50,
                           start_date='2019-06-01',
                           expiry_date='2019-06-30')
        save50.save()

        promotion = Promotion.find(save50.id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, save50.id)
        self.assertEqual(promotion.code, save50.code)
        self.assertEqual(promotion.percentage, save50.percentage)


    def test_add_a_promotion(self):
        """ Create a promotion """
        promotion = Promotion(code="SAVE50",
                              percentage=50,
                              start_date='2019-06-01',
                              expiry_date='2019-06-30')
        promotion.save()
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].code, "SAVE50")

class TestProduct(unittest.TestCase):
    """ Test cases for Products """

    @classmethod
    def setUpClass(cls):
        """ Run once before all test cases """
        app.debug = False

    @classmethod
    def tearDownClass(cls):
        """ Run once after all test cases """
        pass

    def setUp(self):
        """ Runs before each test """
        db = connect('promotion')
        db.drop_database('promotion') # clean up the last tests

    def tearDown(self):
        """ Runs after each test """
        db = connect('promotion')
        db.drop_database('promotion') # clean up the last tests

    def test_product_serialize(self):
        """ Test Product serialization """
        test_id = 'ae12GH1vfg2KC51a'
        self.assertEqual(Product.objects.count(), 0)
        Product(product_id=test_id).save()
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.get(product_id=test_id).serialize()
        self.assertEqual(product['product_id'], test_id)

    def test_delete(self):
        """ Delete a Promotion by ID """
        promotion = Promotion(code='SAVE30',
                              percentage=70,
                              start_date='2019-10-01',
                              expiry_date='2019-11-01')
        promotion.save()
        self.assertEqual(len(Promotion.all()), 1)
        promotion.delete()
        self.assertEqual((len(Promotion.all())), 0)

