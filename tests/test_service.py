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
from unittest.mock import MagicMock, patch
from service.models import Promotion, db
from .promotion_factory import PromotionFactory
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', 'mongodb://localhost/promotion')

######################################################################
#  T E S T   C A S E S
######################################################################

class TestPromotionServer(unittest.TestCase):
    """ Promotion server test case """

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
        self.app = app.test_client()

    def tearDown(self):
        """ Runs after each test """
        db.connection.drop_database('promotion')    # clean up the last tests

    def test_list_all_promotions(self):
        """ Get a list of all Promotions in DB """
        COUNT = 5
        for _ in range(COUNT):
            PromotionFactory().save()
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), COUNT)
    
    def test_get_promotions_by_code(self):
        """ Get a list of all Promotions having a given code """
        PromotionFactory.batch_create(10)
        COUNT = 5
        CODE = 'SAVE_NOTHING'
        for _ in range(COUNT):
            promotion = PromotionFactory()
            promotion.code = CODE
            promotion.save()
        PromotionFactory.batch_create(12)
        resp = self.app.get('/promotions?promotion-code={}'.format(CODE))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), COUNT)
