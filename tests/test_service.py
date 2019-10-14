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
from service.models import Product

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

    def test_apply_a_promotion_on_products(self):
        """ Apply a promotion on a set of products together with their prices """

        # Set up fake data
        product_ids = ['ae12GH1vfg2KC51a', 'c2GH374g2C51dacg', 'c3573HEYv02351dh']
        prices = [200, 352.12, 101.99]
        products = []
        for product_id in product_ids[:-1]: # exclude the last one
            product = Product(product_id)
            product.save()
            products.append(product)
        test_promotion = PromotionFactory()
        test_promotion.products = products
        test_promotion.percentage = 70
        test_promotion.save()

        # Create request json data
        request_data = {'products': []}
        for product_id, price in zip(product_ids, prices):
            request_data['products'].append({'product_id': product_id, 'price': price})

        # Create ground truth
        ground_truth = {}
        eligible_ids = [product['product_id'] for product in test_promotion.products]
        for product_id, price in zip(product_ids, prices):
            if product_id in eligible_ids:
                ground_truth[product_id] = price * (test_promotion.percentage/100.0)
            else:
                ground_truth[product_id] = price

        # Apply promotion
        resp = self.app.post('/promotions/{}/apply'.format(test_promotion.id), 
                            json=request_data, 
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_data = resp.get_json()
        for product in resp_data['products']:
            self.assertEqual(product['price'], ground_truth[product['product_id']])

    def test_apply_a_promotion_with_bad_request_data(self):
        """ Test apply a promotion API with bad request data """

        # Set up fake and bad data
        product_ids = ['ae12GH1vfg2KC51a', 'c2GH374g2C51dacg', 'c3573HEYv02351dh']
        prices = [200, "abc", 101.99]
        nonexist_promotion_id = '666f6f2d6261722d71757578'
        test_promotion = PromotionFactory()
        test_promotion.save()
        test_promotion_id = test_promotion.id
        request_data = {'products': []}
        for product_id, price in zip(product_ids, prices):
            request_data['products'].append({'product_id': product_id, 'price': price})
        print(request_data)

        # Apply promotion with nonexist promotion
        resp = self.app.post('/promotions/{}/apply'.format(nonexist_promotion_id), 
                            json=request_data, 
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Apply promotion with bad products data
        resp = self.app.post('/promotions/{}/apply'.format(test_promotion_id), 
                            json=request_data, 
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.app.post('/promotions/{}/apply'.format(test_promotion_id), 
                            json={'products': {}}, 
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.app.post('/promotions/{}/apply'.format(test_promotion_id), 
                            json={'fake': []}, 
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
