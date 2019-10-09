"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Promotion, DataValidationError, db
from service import app

DATABASE_URI = ""

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
