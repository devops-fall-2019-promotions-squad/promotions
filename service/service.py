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
All service functions should be defined here
"""

import sys
import logging
from datetime import datetime, timedelta
from flask import request, abort, jsonify, url_for, make_response
from flask_api import status    # HTTP Status Codes

from service.models import Promotion

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    #####################################################################
    # This API should display documentation of our APIs.                #
    # But now I used it as an little example for developers.            #
    # This example showed how to add item to DB and iterate through DB. #
    # Again, this is an example. All DB operation should be in          #
    # Promotion class.                                                  #
    #####################################################################

    Promotion(
        code='SAVE15',
        percentage=70,
        start_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=10)
    ).save()
    lst = []
    for promotion in Promotion.objects:
        lst.append(promotion.code)
    return jsonify(lst)


######################################################################
# LIST PROMOTIONS
######################################################################
@app.route('/promotions', methods=['GET'])
def list_promotions():
    """
    List promotions.

    This endpoint will return all promotions if no promotion code is provided.
    If a promotion code is provided, it returns a list of promotions having
    the that promotion code.
    While no promotion is found, no matter a code is provided or not, rather
    than raising a NotFound, we return an empty list to indicate that nothing
    is found.
    """
    code = request.args.get('promotion-code')
    promotions = []
    if code:
        app.logger.info('Request for promotion list with code %s', code)
        promotions = Promotion.find_by_code(code)
    else:
        app.logger.info('Request for promotion list')
        promotions = Promotion.all()

    return make_response(jsonify(promotions), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the MongoDB """
    global app
    Promotion.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')

        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)

        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)

        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
