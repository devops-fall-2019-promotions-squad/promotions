"""
Promotion API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
from service.service import app, initialize_logging
from mongoengine import connect
from .promotion_factory import PromotionFactory

######################################################################
#  T E S T   C A S E S
######################################################################

class TestPromotionServer(unittest.TestCase):
    """ Promotion server test case """

    @classmethod
    def setUpClass(cls):
        """ Run once before all test cases """
        app.debug = False
        initialize_logging(logging.INFO)

    @classmethod
    def tearDownClass(cls):
        """ Run once after all test cases """
        pass

    def setUp(self):
        """ Runs before each test """
        db = connect('promotion')
        db.drop_database('promotion') # clean up the last tests
        self.app = app.test_client()

    def tearDown(self):
        """ Runs after each test """
        db = connect('promotion')
        db.drop_database('promotion') # clean up the last tests

    def test_list_all_promotions(self):
        """ Get a list of all Promotions in DB """
        count = 5
        for _ in range(count):
            PromotionFactory().save()
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), count)

    def test_get_promotions_by_code(self):
        """ Get a list of all Promotions having a given code """
        PromotionFactory.batch_create(10)
        count = 5
        code = 'SAVE_NOTHING'
        for _ in range(count):
            promotion = PromotionFactory()
            promotion.code = code
            promotion.save()
        PromotionFactory.batch_create(12)
        resp = self.app.get('/promotions?promotion-code={}'.format(code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), count)
