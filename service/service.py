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
from flask import request, jsonify, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

from service.models import Promotion, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Promotion REST API Service',
                   version='1.0',
                  ), status.HTTP_200_OK

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

    return make_response(jsonify([p.serialize() for p in promotions]), status.HTTP_200_OK)

######################################################################
# Apply a promotion on products
######################################################################
@app.route('/promotions/<promotion_id>/apply', methods=['POST'])
def apply_a_promotioin(promotion_id):
    """
    Apply a promotion on a given set of products together with their prices

    This endpoint will return those given products with their updated price.
    Products that are not eligible to the given promotion will be returned without any update
    """
    app.logger.info('Apply promotion {%s} to products', promotion_id)
    check_content_type('application/json')
    data = request.get_json()

    # Get promotion data
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))

    # Get product data
    try:
        products = data['products']
        assert(isinstance(products, list))
    except KeyError as error:
        raise DataValidationError('Missing products key in request data')
    except AssertionError as error:
        raise DataValidationError('The given products in request data should be a list of serialized product objects')

    # Apply promotion on products
    products_with_new_prices = []
    eligible_ids = [product['product_id'] for product in promotion.products]
    print(eligible_ids)
    for product in products:
        product_id = product['product_id']
        try:
            price = float(product['price'])
        except ValueError as error:
            raise DataValidationError('The given product prices cannot convert to a float number')
        if product_id in eligible_ids:
            product['price'] = price * (promotion.percentage / 100.0)
        products_with_new_prices.append(product)

    return make_response(jsonify({"products": products_with_new_prices}), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def init_db():
    """ Initializes the MongoDB """
    global app
    Promotion.init_db(app)

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

######################################################################
# READ A PROMOTION
######################################################################
@app.route('/promotions/<promotion_id>', methods=['GET'])
def read_a_promotioin(promotion_id):
    """
    Read a single promotion

    This endpoint will return a Promotion based on it's id
    """
    app.logger.info('Read a promotion with id: %s', promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST