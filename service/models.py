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

import logging
from flask_mongoengine import MongoEngine

# Create the MongoEngine object to be initialized later in init_db()
db = MongoEngine()

class ProductId(db.Document):
    """
    Class that represents a product id. 

    """
    product =  db.StringField(default='')

    def __unicode__(self):
        return self.product

class Stakeholder(db.Document):
    """
    Class that represents a Stakeholder id

    """
    stakeholderid = db.StringField()

    def __unicode__(self):
        return self.product

class Promotion(db.Document):
    """
    Class that represents a Promotion

    This version uses a NoSQL database MongoDB for persistence 
    which is hidden from us by using Mongo Engine
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    # TODO: define the Promotion schema, add field restrictions
    code = db.StringField(default='')
    productids = db.ListField(db.ReferenceField(ProductId))
    percentage = db.IntField(required=True, unique=False)
    expirydate = db.DateTimeField()
    stakeholders = db.ListField(db.ReferenceField(Stakeholder))
    startdate = db.DateTimeField()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize MongoEngine from the Flask app
        db.init_app(app)
        app.app_context().push()