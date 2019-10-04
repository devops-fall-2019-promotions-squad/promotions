import os
import sys
import logging
from flask import Flask, request, abort, jsonify, url_for
from flask_api import status    # HTTP Status Codes

from flask_mongoengine import MongoEngine
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

    Promotion(code='SAVE20').save()
    lst = []
    for promotion in Promotion.objects:
        lst.append(promotion.code)
    return jsonify(lst)

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