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

from service.models import Promotion

# Import Flask application
from . import app

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
#  U T I L I T Y   F U N C T I O N S
######################################################################

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
# LIST ALL APIS
######################################################################
@app.route('/', methods=['GET'])
def list_all_apis():
    """ Root URL response. Returns all of the APIs  """
    app.logger.info('Request for api list')
    func_list = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(rule.methods)
            func_list.append((rule.rule, methods, app.view_functions[rule.endpoint].__doc__))
    return make_response(jsonify(name='Promotion REST API Service',
                                 version='1.0',
                                 functions=func_list), status.HTTP_200_OK)
    