
from itertools import groupby
from fractions import *
from math import (ceil, floor, log, modf, gcd)


def lcm(x, y):
    return (x * y) // gcd(x, y)

def _superior_binary(n):
    x = floor(log(n, 2))
    return 2 ** x









def _is_pow2(n):
    """is n a power of 2?"""
    return modf(log(n, 2))[0] == 0

# def _is_pow2(n):
#     """is n a power of 2?"""
#     return not n & (n - 1)

def nearest_binary(n):
    next_bin = ceil(log(n, 2))
    last_bin = floor(log(n, 2))
    arithmetic_mean = (pow(2, next_bin) + pow(2, last_bin)) // 2
    if n <= arithmetic_mean:
        return int(pow(2, last_bin))
    else:
        return int(pow(2, next_bin))


def are_multiple(a, b):
    if max(a, b) % min(a, b):
        return False
    else:
        return True


def tuplet_label(beat):
    """returns a tuplet label when needed"""
    dnm = beat.denominator
    if _is_pow2(dnm):          # doesn't need tuplet
        tuplet = "", None
    else:
        nearest_bin = nearest_binary(dnm)
        tuplet = "\\tuplet " + str(dnm) + "/" + str(nearest_bin) + " {", dnm
    return tuplet
    
# def tuplet_label(beat, instead_of=None):
#     """returns a tuplet label when needed"""
#     dnm = beat.denominator
#     if _is_pow2(dnm):          # doesn't need tuplet
#         return ""
#     else:
#         if instead_of:
#             tuplet = "\\tuplet " + str(dnm) + "/" + str(instead_of) + " {"
#         else:
#             nearest_bin = nearest_binary(dnm)
#             tuplet = "\\tuplet " + str(dnm) + "/" + str(nearest_bin) + " {"
#         return tuplet

# def superior_x(x, L):
#     """"""
#     l = L + [maxsize]
#     for i, n in enumerate(l):
#         if x == n:
#             return n
#         elif x < n:
#             return l[i - 1]

def superior_x(x, L):
    le = list(filter(lambda i: i <= x, L))
    if le:
        return le[-1]
    else:
        return None

        
def factorize(n):
    """prime factors of n"""
    if n < 2:
        return None
    factors = []
    divisor = 2
    while True:
        if pow(divisor, 2) > n:
            factors.append(n)
            return factors
        elif n % divisor == 0:
            n //= divisor
            factors.append(divisor)
        else:
            divisor += 1

def disassemble_rhythm(n_notes, lily_beat_unit, timesig=None):
    """returns a list of (n, lily_beat_units) of the input rhythm.
    If timesig is provided output is a two-element tuple
    with the second one being the possible full measure rest."""
    d, m = divmod(n_notes, lily_beat_unit)
    out = [(int(d), 1)]
    while m > 0:
        sup_bin = _superior_binary(m)
        d, m = divmod(m, sup_bin)
        v = int(lily_beat_unit / sup_bin)
        out.append((int(d), v))
    
    out = list(filter(lambda l: l[0], out))

    # Provide only if you know you have rests!
    # And want full measure rests.
    if timesig:
        if (n_notes, lily_beat_unit) == timesig:
            full_measure_rest = "R1*{}/{}".format(*timesig)
        else:
            full_measure_rest = None
        return out, full_measure_rest
    else:
        return out


