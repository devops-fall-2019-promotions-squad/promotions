
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
    id = factory.Sequence(lambda n: n)
    code = factory.Faker('promotion_code')
    percentage = FuzzyChoice(choices=[10, 40, 110, 25, 5, 0, 200, -10])
    expiry_date = FuzzyChoice(choices=['11-11-2019', '04-01-2018', '01-10-2019', '03-05-2020'])
    start_date = FuzzyChoice(choices=['11-11-2019', '04-01-2018', '01-10-2019', '03-05-2020'])

if __name__ == '__main__':
    for _ in range(10):
        pet = PromotionFactory()
        print(pet.serialize())