"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import json
from service import app
from service.models import Promotion, DataValidationError
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

    def setUp(self):
        """ Runs before each test """
        Promotion.init_db("test")
        Promotion.remove_all()

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
                  products=[],
                  start_date='2019-10-01',
                  expiry_date='2019-11-01').save()
        save50 = Promotion(code="SAVE50",
                           percentage=50,
                           products=[],
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
                              products=[],
                              start_date='2019-06-01',
                              expiry_date='2019-06-30')
        promotion.save()
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].code, "SAVE50")

    def test_promotion_deserialize(self):
        """ Test Promotion deserialization"""
        promotion = PromotionFactory()
        json_data = json.dumps(dict(
            code=promotion.code,
            percentage=promotion.percentage,
            expiry_date=promotion.expiry_date,
            start_date=promotion.start_date,
            products=promotion.products
        ))
        promotion_deserialized = Promotion()
        promotion_deserialized.deserialize(json.loads(json_data))
        self.assertEqual(promotion.code, promotion_deserialized.code)
        self.assertEqual(promotion.percentage,
                         promotion_deserialized.percentage)
        self.assertEqual(promotion.expiry_date,
                         promotion_deserialized.expiry_date)
        self.assertEqual(promotion.start_date,
                         promotion_deserialized.start_date)

    def test_promotion_deserialize_exceptions(self):
        """ Test Promotion deserialization exceptions"""
        promotion = PromotionFactory()
        json_data = json.dumps(dict(
            percentage=promotion.percentage,
            start_date=promotion.start_date,
        ))
        promotion_deserialized = Promotion()
        try:
            promotion_deserialized.deserialize(json.loads(json_data))
        except DataValidationError:
            self.assertRaises(DataValidationError)

        json_data = json.dumps(dict(
            code=promotion.code,
            percentage=promotion.percentage,
            expiry_date="shouldn't like this",
            start_date=promotion.start_date,
            products=promotion.products
        ))
        promotion_deserialized = Promotion()
        try:
            promotion_deserialized.deserialize(json.loads(json_data))
        except DataValidationError:
            self.assertRaises(DataValidationError)

    def test_promotion_save_exceptions(self):
        """ Test Promotion save exceptions"""
        promotion = PromotionFactory()
        promotion.percentage = 131
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion.percentage = -12
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.code = ''
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.code = None
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.percentage = None
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.products = None
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.expiry_date = None
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

        promotion = PromotionFactory()
        promotion.start_date = None
        try:
            promotion.save()
        except DataValidationError:
            self.assertRaises(DataValidationError)

    def test_delete_nonexist(self):
        """ Test deleting a nonexist Promotion"""
        promotion = PromotionFactory()
        promotion.id = '1cak41-nonexist'
        try:
            promotion.delete()
        except KeyError:
            self.assertRaises(KeyError)

    def test_update_nonexist(self):
        """ Test deleting a nonexist Promotion"""
        promotion = PromotionFactory()
        promotion.id = '1cak41-nonexist'
        try:
            promotion.update()
        except KeyError:
            self.assertRaises(KeyError)
