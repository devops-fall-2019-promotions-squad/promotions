
"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion

class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        model = Promotion
    code = FuzzyChoice(choices=['SAVE15', 'SAVE20', 'SAVE30'])
    percentage = FuzzyChoice(choices=[10, 40, 30, 25, 5, 0, 15])
    expiry_date = FuzzyChoice(choices=['11-11-2019', '04-01-2018', '01-10-2019', '03-05-2020'])
    start_date = FuzzyChoice(choices=['11-11-2019', '04-01-2018', '01-10-2019', '03-05-2020'])

    @classmethod
    def batch_create(cls, count):
        """ Factory method to create promotions in bulk """
        fakers = []
        for _ in range(count):
            faker = PromotionFactory()
            faker.save()
            fakers.append(faker)
        return fakers
