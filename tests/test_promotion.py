"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Promotion, db
from service import app
from .promotion_factory import PromotionFactory
from datetime import datetime

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
        pass

    def setUp(self):
        """ Runs before each test """
        db.connection.drop_database('promotion')    # clean up the last tests

    def tearDown(self):
        """ Runs after each test """
        db.connection.drop_database('promotion')    # clean up the last tests

    def test_find(self):
        """ Find a Promotion by ID """
        Promotion(code='SAVE30',
                  percentage=70,
                  start_date='2019-10-01',
                  expiry_date='2019-11-01').save()
        save50 = Promotion(code="SAVE50",
                           percentage = 50,
                           start_date='2019-06-01',
                           expiry_date='2019-06-30')
                          
        save50.save()

        promotion = Promotion.find(save50.id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, save50.id)
        self.assertEqual(promotion.code, save50.code)
        self.assertEqual(promotion.percentage, save50.percentage)