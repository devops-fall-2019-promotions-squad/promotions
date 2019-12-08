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

import os
import sys
import time
import json
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError
from cloudant.adapters import Replay429Adapter

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')


class DatabaseConnectionError(Exception):
    """ Custom Exception when database connection fails """


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Promotion():
    """
    Class that represents a Promotion

    This version uses a NoSQL database CouchDB for persistence
    which is hidden from us by using Cloudant library
    """
    logger = logging.getLogger('flask.app')
    client = None   # cloudant.client.Cloudant
    database = None  # cloudant.database.CloudantDatabase

    def __init__(self, code=None, products=None,
                 percentage=None, expiry_date=None, start_date=None):
        """ Constructor """
        self.id = None
        self.code = code
        self.products = products
        self.percentage = percentage
        self.expiry_date = expiry_date
        self.start_date = start_date

    def create(self):
        """
        Creates a new Promotion in the database
        """
        self.validate()

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Promotion.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']

    def update(self):
        """ Updates a Promotion in the database """
        self.validate()

        if self.id:
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.update(self.serialize())
                document.save()

    def save(self):
        """ Saves a Promotion in the database """
        if self.id:
            self.update()
        else:
            self.create()

    def delete(self):
        """ Deletes a Promotion from the database """
        if self.id:
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.delete()

    def validate(self):
        """ object fields validation """
        if self.code is None or self.code == '':
            raise DataValidationError('code attribute is not set')
        if self.products is None:
            raise DataValidationError('products attribute is not set')
        if self.percentage is None:
            raise DataValidationError('percentage attribute is not set')
        if self.expiry_date is None:
            raise DataValidationError('expiry_date attribute is not set')
        if self.start_date is None:
            raise DataValidationError('start_date attribute is not set')
        if self.start_date > self.expiry_date:
            raise DataValidationError('start date should not be larger than expiry date')
        if self.percentage < 0 or self.percentage > 100:
            raise DataValidationError(
                'Percentage should be in the range of 0 to 100')

        # Check if this promotion conflicts with any existing promotions
        promotions = Promotion.find_by_code(self.code)
        for promotion in promotions:
            if self.id is not None and self.id == promotion.id:
                continue

            if (promotion.start_date <= self.start_date and self.start_date <= promotion.expiry_date) or \
                (promotion.start_date <= self.expiry_date and self.expiry_date <= promotion.expiry_date):
                raise DataValidationError(f'This new/updated promotion conflicts with promotion({promotion.id})')

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id,
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
            self.percentage = int(data['percentage'])
            self.expiry_date = int(data['expiry_date'])
            self.start_date = int(data['start_date'])
            self.products = data['products']
        except KeyError as error:
            raise DataValidationError(
                'Invalid promotion: missing ' + error.args[0])
        except ValueError as error:
            raise DataValidationError(
                'Invalid promotion value: ' + error.args[0])

        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']

        return self
    
    def is_active(self):
        """
        A promotion is active if the current timestamp is in its range [start_date, expiry_date]
        """
        now_ts = time.time()
        return self.start_date <= now_ts and now_ts <= self.expiry_date

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################
    @classmethod
    def connect(cls):
        """ Connect to the server """
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """ Disconnect from the server """
        cls.client.disconnect()

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    def all(cls):
        """ Query that returns all Promotions """
        results = []
        for doc in cls.database:
            promotion = Promotion().deserialize(doc)
            promotion.id = doc['_id']
            results.append(promotion)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################
    @classmethod
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            pet = Promotion()
            pet.deserialize(doc)
            results.append(pet)
        return results

    @classmethod
    def find(cls, promotion_id):
        """ Query that finds Promotions by their id """
        try:
            document = cls.database[promotion_id]
        except KeyError:
            return None
        if '_rev' in document:
            return Promotion().deserialize(document)
        return None

    @classmethod
    def find_by_code(cls, code):
        """ Query that finds Promotions by their code """
        return cls.find_by(code=code)

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################
    @staticmethod
    def init_db(dbname='promotions'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        vcap_services = {}
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Promotion.logger.info('Running in Bluemix mode.')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        elif 'BINDING_CLOUDANT' in os.environ:
            Promotion.logger.info('Found Kubernetes Bindings')
            creds = json.loads(os.environ['BINDING_CLOUDANT'])
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
        else:
            Promotion.logger.info(
                'VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            creds = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

        # Look for Cloudant in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('cloudantNoSQLDB'):
                cloudant_service = vcap_services[service][0]
                opts['username'] = cloudant_service['credentials']['username']
                opts['password'] = cloudant_service['credentials']['password']
                opts['host'] = cloudant_service['credentials']['host']
                opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = cloudant_service['credentials']['url']

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            raise DatabaseConnectionError('Error - Failed to retrieve options. '
                                          'Check that app is bound to a Cloudant service.')

        Promotion.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Promotion.logger.info('Running in Admin Party Mode...')
            Promotion.client = Cloudant(opts['username'],
                                        opts['password'],
                                        url=opts['url'],
                                        connect=True,
                                        auto_renew=True,
                                        admin_party=ADMIN_PARTY,
                                        adapter=Replay429Adapter(
                                            retries=10, initialBackoff=0.1)
                                        )
        except ConnectionError:
            raise DatabaseConnectionError(
                'Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Promotion.database = Promotion.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Promotion.database = Promotion.client.create_database(dbname)
        # check for success
        if not Promotion.database.exists():
            raise DatabaseConnectionError(
                'Database [{}] could not be obtained'.format(dbname))
