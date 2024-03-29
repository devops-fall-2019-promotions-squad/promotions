"""
Environment for Behave Testing
"""
import os
from behave import *
from selenium import webdriver

WAIT_SECONDS = 120
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

def before_all(context):
    """ Executed once before all tests """

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized") # open Browser in maximized mode
    options.add_argument("disable-infobars") # disabling infobars
    options.add_argument("--disable-extensions") # disabling extensions
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--headless")
    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(WAIT_SECONDS) # seconds

    context.base_url = BASE_URL
    context.config.setup_logging()


def after_all(context):
    """ Executed after all tests """
    context.driver.quit()
