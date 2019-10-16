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
from unittest.mock import patch
from flask_api import status    # HTTP Status Codes
from mongoengine import connect

from datetime import datetime
from service.service import app, initialize_logging
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
            expiry_date=promotion.expiry_date.strftime("%m-%d-%Y"),
            start_date=promotion.start_date.strftime("%m-%d-%Y"),
            products=promotion.products
        )), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location is not None)
        # Check the data is correct
        new_prom = resp.get_json()
        self.assertEqual(new_prom['code'], promotion.code, "Codes do not match")
        self.assertEqual(new_prom['percentage'], promotion.percentage, "Percentage do not match")
        self.assertEqual(new_prom['expiry_date'], promotion.expiry_date.strftime("%m-%d-%Y"), "Expiry date does not match")
        self.assertEqual(new_prom['start_date'], promotion.start_date.strftime("%m-%d-%Y"), "Start date does not match")
        self.assertTrue(set(promotion.products) == set(new_prom['products']))
        # Check that the location header was correct
        resp = self.app.get(location, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_prom = resp.get_json()
        self.assertEqual(new_prom['code'], promotion.code, "Codes do not match")
        self.assertEqual(new_prom['percentage'], promotion.percentage, "Percentage do not match")
        self.assertEqual(new_prom['expiry_date'], promotion.expiry_date.strftime("%m-%d-%Y"), "Expiry date does not match")
        self.assertEqual(new_prom['start_date'], promotion.start_date.strftime("%m-%d-%Y"), "Start date does not match")
        self.assertTrue(set(promotion.products) == set(new_prom['products']))

    def test_apply_a_promotion_on_products(self):
        """ Apply a promotion on a set of products together with their prices """

        # Set up fake data
        product_ids = ['ae12GH1vfg2KC51a', 'c2GH374g2C51dacg', 'c3573HEYv02351dh']
        prices = [200, 352.12, 101.99]
        products = product_ids[:-1]
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
        eligible_ids = test_promotion.products
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

    def test_update_a_promotion(self):
        """ Update a promotion, given a promotion id """
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post('/promotions', 
                            json=test_promotion.serialize(), 
                            content_type = 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #update a promotion
        new_promotion = resp.get_json()
        new_promotion['code'] = 'SAVENEW'
        resp = self.app.put('/promotions/{}'.format(new_promotion['id']),
                            json=new_promotion, 
                            content_type = 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion['code'], 'SAVENEW')
        self.assertEqual(updated_promotion['id'], new_promotion['id'])
    
    def test_update_a_nonexist_promotion(self):
        """ Update a promotion, given a nonexist promotion id """
        fake_test_promotion_id = '666f6f2d6261722d71757578'

        #update a promotion
        resp = self.app.put('/promotions/{}'.format(fake_test_promotion_id),
                            json={}, 
                            content_type = 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

        resp = self.app.post('/promotions/{}/apply'.format(test_promotion_id),
                             json={'fake': []},
                             content_type='application/xml')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,)

    def test_delete_a_promotion(self):
        """ Delete a promotion by given ID """
        test_promotion = PromotionFactory()
        test_promotion.save()
        resp = self.app.delete('/promotions/{}'.format(test_promotion.id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_all_apis(self):
        """ List all APIs """
        resp = self.app.get('/', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        api_cnt = len(list(app.url_map.iter_rules())) - 1 # exclude static
        self.assertEqual(len(data['functions']), api_cnt)

    def test_invalid_method_request(self):
        """ Testing invalid HTTP method request """
        resp = self.app.post('/') # this route only support GET
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('service.models.Promotion.all')
    def test_500_internal_server_error_request(self, list_all_mock):
        """ Test a 500 internal server error request """
        # let Promotion all function return a Exception to case a 500 error
        list_all_mock.side_effect = Exception()
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
