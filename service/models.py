#                               _
#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                           O\  =  /O
#                        ____/`---'\____
#                      .'  \\|     |//  `.
#                     /  \\|||  :  |||//  \
#                    /  _||||| -:- |||||_  \
#                    |   | \\\  -  /'| |   |
#                    | \_|  `\`---'//  |_/ |
#                    \  .-\__ `-. -'__/-.  /
#                  ___`. .'  /--.--\  `. .'___
#               ."" '<  `.___\_<|>_/___.' _> \"".
#              | | :  `- \`. ;`. _/; .'/ /  .' ; |
#              \  \ `-.   \_\_`. _.'_/_/  -' _.' /
#    ===========`-.`___`-.__\ \___  /__.-'_.'_.-'================
#                            `=--=-'                    BUG FREE
"""
All models should be defined here
"""

import logging
# Create the MongoEngine object to be initialized later in init_db()
from mongoengine import Document, ValidationError, StringField, ListField, \
    ReferenceField, IntField, DateTimeField, connect

class Validation:
    """
    Class that wraps up all DB validation functions
    """
    @classmethod
    def valid_code(cls, code):
        """ Code value should be non-empty """
        if not code:
            raise ValidationError('Promotion code should be non-empty')

    @classmethod
    def valid_perc(cls, percentage):
        """ Check if the given precentage value is in range 0 to 100 """
        if percentage < 0 or percentage > 100:
            raise ValidationError('Percentage should be in the range of 0 to 100')

class Product(Document):
    """
    Class that represents a product id
    """
    product_id = StringField(default='')

class Promotion(Document):
    """
    Class that represents a Promotion

    This version uses a NoSQL database MongoDB for persistence
    which is hidden from us by using Mongo Engine
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    code = StringField(required=True, validation=Validation.valid_code)
    products = ListField(ReferenceField(Product))
    percentage = IntField(required=True, unique=False, validation=Validation.valid_perc)
    expiry_date = DateTimeField(required=True)
    start_date = DateTimeField(required=True)

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        cls.logger.info('Processing all Promotions')
        return cls.objects()

    @classmethod
    def find_by_code(cls, code):
        """ Find a list of promotions having the given a promotion code """
        cls.logger.info('Find promotions by code %s', code)
        return cls.objects(code=code)

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize MongoEngine from the Flask app
        connect('promotion')
        app.app_context().push()
