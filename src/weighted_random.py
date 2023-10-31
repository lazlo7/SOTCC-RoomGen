# Weighted random distribution test implementation.
from typing import TypeAlias, TypeVar
from collections.abc import Iterable
from random import random
from itertools import starmap

T = TypeVar("T")
Weighted: TypeAlias = tuple[int, T] 

class WeightedRandom:
    def __init__(self, weighted_items: Iterable[Weighted]):
        weights_sum = sum(starmap(lambda w, _: w, weighted_items))
        cum_sum = 0
        self._weights = []
        for weight, item in weighted_items:
            cum_sum += weight / weights_sum
            self._weights.append((cum_sum, item))

    def next(self) -> T:
        return self._find_item(random())
    
    def _find_item(self, value: float) -> T:
        l = 0
        r = len(self._weights) - 1
        while l < r:
            mid = l + (r - l) // 2
            if value < self._weights[mid][0]:
                r = mid
            else:
                l = mid + 1
        return self._weights[r][1]

if __name__ == "__main__":
    wr = WeightedRandom([(100, "Regular"), (40, "Spiked"), (20, "Poisoned"), (10, "Explosive"), (3, "Demon")])
    print("Generated traps:")
    for i in range(20):
        print(f"{i + 1}. {wr.next()}")