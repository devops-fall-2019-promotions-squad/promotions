"""
Promotion API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import json
import logging
from flask_api import status    # HTTP Status Codes
from service.service import app, initialize_logging
from mongoengine import connect
from datetime import datetime
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
        db.drop_database('promotion')  # clean up the last tests
        self.app = app.test_client()

    def tearDown(self):
        """ Runs after each test """
        db = connect('promotion')
        db.drop_database('promotion')  # clean up the last tests

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

    def test_read_a_promotion(self):
        """ Read a promotion by given ID """
        test_promotion = PromotionFactory()
        test_promotion.save()
        resp = self.app.get('/promotions/{}'.format(test_promotion.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['code'], test_promotion.code)

    def test_read_a_promotion_not_found(self):
        """ Read a promotion that is not found """
        resp = self.app.get('/promotions/{}'.format('666f6f2d6261722d71757578'))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_a_promotion(self):
        """ Add a promotion """
        promotion = PromotionFactory()
        resp = self.app.post('/promotions', data=json.dumps(dict(
            code=promotion.code,
            percentage=promotion.percentage,
            expiry_date=promotion.expiry_date,
            start_date=promotion.start_date,
        )), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location is not None)
        # Check the data is correct
        new_prom = resp.get_json()
        self.assertEqual(new_prom['code'], promotion.code, "Codes do not match")
        self.assertEqual(new_prom['percentage'], promotion.percentage, "Percentage do not match")
        self.assertEqual(new_prom['expiry_date'], promotion.expiry_date, "Expiry date does not match")
        self.assertEqual(new_prom['start_date'], promotion.start_date, "Start date does not match")
        # Check that the location header was correct
        resp = self.app.get(location, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_prom = resp.get_json()
        self.assertEqual(new_prom['code'], promotion.code, "Codes do not match")
        self.assertEqual(new_prom['percentage'], promotion.percentage, "Percentage do not match")
        self.assertEqual(new_prom['expiry_date'], promotion.expiry_date, "Expiry date does not match")
        self.assertEqual(new_prom['start_date'], promotion.start_date, "Start date does not match")
