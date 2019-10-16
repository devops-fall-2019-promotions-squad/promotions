
"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion, Product
import datetime

class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        """ Meta class for Promotion Factory """
        model = Promotion
    code = FuzzyChoice(choices=['SAVE15', 'SAVE20', 'SAVE30'])
    percentage = FuzzyChoice(choices=[10, 40, 30, 25, 5, 0, 15])
    expiry_date = FuzzyChoice(choices=[datetime.datetime(year=2019, month=11, day=11), datetime.datetime(year=2018, month=1, day=4), datetime.datetime(year=2019, month=10, day=1), datetime.datetime(year=2020, month=5, day=3)])
    start_date = FuzzyChoice(choices=[datetime.datetime(year=2019, month=10, day=9), datetime.datetime(year=2018, month=11, day=2), datetime.datetime(year=2019, month=3, day=20), datetime.datetime(year=2018, month=5, day=13)])
    products = list(map(lambda prod: (lambda p: [p, p.save()][0])(Product(product_id=prod)), ['MacBook', 'Airpods']))

    @classmethod
    def batch_create(cls, count):
        """ Factory method to create promotions in bulk """
        fakers = []
        for _ in range(count):
            faker = PromotionFactory()
            faker.save()
            fakers.append(faker)
        return fakers
