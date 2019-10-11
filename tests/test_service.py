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
        initialize_logging(logging.INFO)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        db.connection.drop_database('promotion')    # clean up the last tests
        self.app = app.test_client()

    def tearDown(self):
        """ Runs after each test """
        db.connection.drop_database('promotion')    # clean up the last tests

    def test_read_a_promotioin(self):
        """ Read a promotion by given ID """
        test_promotion = PromotionFactory()
        test_promotion.save()
        resp = self.app.get('/promotions/{}'.format(test_promotion.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['code'], test_promotion.code)
