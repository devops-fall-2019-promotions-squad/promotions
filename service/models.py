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
from flask_mongoengine import MongoEngine

# Create the MongoEngine object to be initialized later in init_db()
db = MongoEngine()

class Validation:
    """
    Class that wraps up all DB validation functions
    """
    @classmethod
    def valid_code(cls, code):
        """ Code value should be non-empty """
        if not code:
            raise db.ValidationError('Promotion code should be non-empty')

    @classmethod
    def valid_perc(cls, percentage):
        """ Check if the given precentage value is in range 0 to 100 """
        if percentage < 0 or percentage > 100:
            raise db.ValidationError('Percentage should be in the range of 0 to 100')

class Product(db.Document):
    """
    Class that represents a product id
    """
    product_id = db.StringField(default='')

class Stakeholder(db.Document):
    """
    Class that represents a Stakeholder id
    """
    stakeholder_id = db.StringField()

class Promotion(db.Document):
    """
    Class that represents a Promotion

    This version uses a NoSQL database MongoDB for persistence
    which is hidden from us by using Mongo Engine
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    code = db.StringField(required=True, validation=Validation.valid_code)
    products = db.ListField(db.ReferenceField(Product))
    percentage = db.IntField(required=True, unique=False, validation=Validation.valid_perc)
    expiry_date = db.DateTimeField(required=True)
    stakeholders = db.ListField(db.ReferenceField(Stakeholder))
    start_date = db.DateTimeField(required=True)

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize MongoEngine from the Flask app
        db.init_app(app)
        app.app_context().push()
