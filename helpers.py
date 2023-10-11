import math
from random import Random

MAX_RANGE = int(math.pow(2, 16) - 1)
NEXT_RANGE = 10000


def generate_random_number(seq):
    return int((Random().randint(1, MAX_RANGE) + seq) % MAX_RANGE)