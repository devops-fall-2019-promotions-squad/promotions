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
Promotion Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /promotions - Returns a list all of the Promotions
GET /promotions/{promotion_id} - Returns the Promotion with a given id number
POST /promotions - creates a new Promotion record in the database
PUT /promotions/{promotion_id} - updates a Promotion record in the database
DELETE /promotions/{promotion_id} - deletes a Promotion record in the database
"""

import logging
import sys

from flask import abort, jsonify, make_response, request, url_for

from flask_api import status  # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs
from service.models import DataValidationError, DatabaseConnectionError, Promotion

# Import Flask application
from . import app


######################################################################
# VISIT INDEX PAGE
######################################################################
# Route to '/' has to be placed before Swagger docs
@app.route('/', methods=['GET'])
def index():
    """ Root URL response. Send back the promotion index page.  """
    return app.send_static_file('index.html')


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app, 
          version='1.0.0', 
          title='Promotion Demo REST API Service', 
          description='This is a sample Promotion server.',
          default='promotions',
          default_label='Promotion operations',
          doc='/apidocs/',
          )

promotion_model = api.model('Promotion', {
    'id': fields.String(readOnly=True,
                         description='The unique id assigned internally by service.'),
    'code': fields.String(required=True,
                          description='The code of the Promotion.'),
    'percentage': fields.Integer(required=True,
                                description='The percentage of the Promotion, 0 < percentage < 100.'),
    'products': fields.List(fields.String, required=True,
                                  description='Product IDs for the Promotion.'),
    'start_date': fields.Integer(required=True,
                                description='Start date timestamp for the Promotion.'),
    'expiry_date': fields.Integer(required=True,
                                 description='Expiry date timestamp for the Promotion.')
})

create_model = api.model('Promotion', {
    'code': fields.String(required=True,
                          description='The code of the Promotion.'),
    'percentage': fields.Integer(required=True,
                                description='The percentage of the Promotion, 0 < percentage < 100.'),
    'products': fields.List(fields.String, required=True,
                                 description='Product IDs for the Promotion.'),
    'start_date': fields.Integer(required=True,
                                description='Start date timestamp for the Promotion.'),
    'expiry_date': fields.Integer(required=True,
                                 description='Expiry date timestamp for the Promotion.')
})

product_model = api.model('Product', {
    'product_id': fields.String(required=True,
                          description='The unique id of the Product.'),
    'price': fields.Float(required=True,
                          description='The price of the Product.'),
})

product_list_model = api.model('Product List', {
    'products': fields.List(fields.Nested(product_model), required=True,
                            description='A list of products.'),
})

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument('promotion-code', type=str, required=False,
                            help='List Promotions by code', location='args')
#####################################################################
# PATH: /promotions
#####################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotion """
    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.expect(promotion_args, validate=True)
    def get(self):
        """
        List promotions.

        This endpoint will return all promotions if no promotion code is provided.
        If a promotion code is provided, it returns a list of promotions having
        the that promotion code.
        While no promotion is found, no matter a code is provided or not, rather
        than raising a NotFound, we return an empty list to indicate that nothing
        is found.
        """
        app.logger.info('Request to list Promotions...')
        args = promotion_args.parse_args()
        code = args['promotion-code']
        promotions = []
        if code:
            app.logger.info('Request for promotion list with code %s', code)
            promotions = Promotion.find_by_code(code)
        else:
            app.logger.info('Request for promotion list')
            promotions = Promotion.all()

        return make_response(jsonify([p.serialize() for p in promotions]), status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc('create_a_promotion')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Promotion created successfully')
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Add a promotion

        This endpoint will return a Promotion based on it's id and the URL to that promotion
        """
        app.logger.info('Request to create a Promotion')
        check_content_type('application/json')
        promotion = Promotion()
        app.logger.debug('Payload = %s', api.payload)
        promotion.deserialize(api.payload)
        promotion.save()
        message = promotion.serialize()
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True)

        return message, status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /promotions/{promotion_id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion{promotion_id} - Returns a Promotion with the promotion_id
    PUT /promotion{promotion_id} - Update a Promotion with the promotion_id
    DELETE /promotion{promotion_id} -  Deletes a Promotion with the promotion_id
    """
    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('read_a_promotion')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion

        This endpoint will return a Promotion based on it's id
        """
        app.logger.info(
            "Request to Retrieve a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "404 Not Found: Promotion with id '{}' was not found.".format(
                          promotion_id)
                      )

        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc('update_a_promotion')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info(
            'Request to update promotion with promotion id {}'.format(promotion_id))
        check_content_type('application/json')
        promotion = Promotion.find(promotion_id)
        if not promotion:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Promotion with id '{}' was not found.".format(promotion_id))
        promotion.deserialize(request.get_json())
        promotion.id = promotion_id
        promotion.save()
        app.logger.info(
            'Promotion with id {} successfully updated'.format(promotion_id))
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('delete_promotions', security='apikey')
    @api.response(204, 'Promotion deleted')
    def delete(self, promotion_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info(
            'Request to Delete a promotion with id [%s]', promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions/{promotion_id}/apply
######################################################################
@api.route('/promotions/<promotion_id>/apply')
@api.param('promotion_id', 'The Promotion identifier')
class ApplyResource(Resource):
    """ Apply actions on a Promotion """
    @api.doc('apply_a_promotion')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted action data was not valid')
    @api.expect(product_list_model)
    @api.marshal_with(product_list_model)
    def post(self, promotion_id):
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
            api.abort(status.HTTP_404_NOT_FOUND,
                      'Promotion with id "{}" was not found.'.format(promotion_id))

        # Check promotion availability
        if not promotion.is_active():
            api.abort(status.HTTP_409_CONFLICT, 'Promotion with id "{}" is not active.'.format(promotion_id))

        # Get product data
        try:
            products = data['products']
            assert isinstance(products, list)
        except KeyError:
            raise DataValidationError('Missing products key in request data')
        except AssertionError:
            raise DataValidationError('The given products in request data \
                should be a list of serialized product objects')

        # Apply promotion on products
        products_with_new_prices = []
        eligible_ids = promotion.products
        non_eligible_ids = []
        print(eligible_ids)
        for product in products:
            product_id = product['product_id']
            try:
                new_price = float(product['price'])
            except ValueError:
                raise DataValidationError(
                    'The given product prices cannot convert to a float number')
            if product_id in eligible_ids:
                new_price = new_price * (promotion.percentage / 100.0)
            else:
                non_eligible_ids.append(product_id)
            product['price'] = new_price
            products_with_new_prices.append(product)

        if len(non_eligible_ids) > 0:
            app.logger.info('The following products are not \
                eligible to the given promotion: %s', non_eligible_ids)

        return {"products": products_with_new_prices}, status.HTTP_200_OK


######################################################################
# LIST ALL APIS
######################################################################
@app.route('/apis', methods=['GET'])
def list_all_apis():
    """ Returns all of the APIs  """
    app.logger.info('Request for api list')
    func_list = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(rule.methods)
            func_list.append(
                (rule.rule, methods, app.view_functions[rule.endpoint].__doc__))
    return make_response(jsonify(name='Promotion REST API Service',
                                 version='1.0',
                                 functions=func_list), status.HTTP_200_OK)


######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
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

######################################################################
# DELETE ALL PROMOTION DATA (for testing only)
######################################################################
@app.route('/promotions/reset', methods=['DELETE'])
def promotions_reset():
    """ Removes all promotions from the database """
    Promotion.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)
