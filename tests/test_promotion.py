"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
from service.models import Promotion, db
from service import app
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
        db.connection.drop_database('promotion')    # clean up the last tests

    def tearDown(self):
        """ Runs after each test """
        db.connection.drop_database('promotion')    # clean up the last tests

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
