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
    ReferenceField, IntField, DateTimeField, connect, DoesNotExist
from datetime import datetime

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

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": str(self.id),
            "code": self.code,
            "products": self.products,
            "percentage": self.percentage,
            "expiry_date": self.expiry_date,
            "start_date": self.start_date,
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the Promotion data
        """
        try:
            self.code = data['code']
            self.percentage = data['percentage']
            self.expiry_date = datetime.fromtimestamp(int(data['expiry_date']))
            self.start_date = datetime.fromtimestamp(int(data['start_date']))
        except KeyError as error:
            self.logger.info('Invalid promotion: missing ' + error.args[0])
        except TypeError:
            self.logger.info('Invalid promotion: body of request contained bad or no data')
        except OverflowError or OSError:
            self.logger.info('Invalid start time or expiry time')
        return self

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

    @classmethod
    def find(cls, promotion_id):
        """ Read a promotions by it's ID """
        cls.logger.info('Processing lookup for id %s', promotion_id)
        try:
            promotion = cls.objects.get(id=promotion_id)
            return promotion
        except DoesNotExist:
            return None
