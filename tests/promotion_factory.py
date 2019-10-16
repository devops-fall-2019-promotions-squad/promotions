
"""
Test Factory to make fake objects for testing
"""
import datetime

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion
from datetime import datetime


class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        """ Meta class for Promotion Factory """
        model = Promotion
    code = FuzzyChoice(choices=['SAVE15', 'SAVE20', 'SAVE30'])
    percentage = FuzzyChoice(choices=[10, 40, 30, 25, 5, 0, 15])
    expiry_date = FuzzyChoice(choices=[datetime.strptime(
        date, "%Y-%m-%d") for date in ['2019-11-11', '2018-01-04', '2019-10-01', '2020-05-03']])
    start_date = FuzzyChoice(choices=[datetime.strptime(
        date, "%Y-%m-%d") for date in ['2019-10-09', '2018-11-02', '2019-03-20', '2020-05-13']])
    products = FuzzyChoice(
        choices=[['MacBook', 'Airpods'], ['iPhone', 'iPad']])

    @classmethod
    def batch_create(cls, count):
        """ Factory method to create promotions in bulk """
        fakers = []
        for _ in range(count):
            faker = PromotionFactory()
            faker.save()
            fakers.append(faker)
        return fakers
