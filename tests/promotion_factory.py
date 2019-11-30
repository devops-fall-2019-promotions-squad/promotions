
"""
Test Factory to make fake objects for testing
"""
from datetime import datetime, timedelta
import random
from collections import defaultdict

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion


class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        """ Meta class for Promotion Factory """
        model = Promotion
    code = FuzzyChoice(choices=['SAVE15', 'SAVE20', 'SAVE30'])
    percentage = FuzzyChoice(choices=[10, 40, 30, 25, 5, 0, 15])
    start_date = int((datetime.now()-timedelta(weeks=random.randint(1, 5))).timestamp())
    expiry_date = int((datetime.now()+timedelta(weeks=random.randint(1, 5))).timestamp())
    products = FuzzyChoice(
        choices=[['5612234', '8516634'], ['847153', '645382']])

    @classmethod
    def batch_create(cls, count, **kwargs):
        """
        Factory method to create promotions in bulk.
        Ensure that promotions with the same code will not overlap with each others
        """
        promotions = cls.create_batch(count, **kwargs)
        promotions_dict = defaultdict(list)
        for promotion in promotions:
            promotions_dict[promotion.code].append(promotion)

        promotions = []
        for promos in promotions_dict.values():
            pre_expiry_date = promos[0].expiry_date
            promos[0].save()
            for promotion in promos[1:]:
                delta = promotion.expiry_date-promotion.start_date
                promotion.start_date = pre_expiry_date+random.randint(100, 2000)
                promotion.expiry_date = promotion.start_date+delta
                pre_expiry_date = promotion.expiry_date
                promotion.save()
            promotions.extend(promos)
        return promotions
