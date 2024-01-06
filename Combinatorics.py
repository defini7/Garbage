"""
Is order important?
    Yes
        Are all of the elements are used?
            Yes
                Permutations
                    Repeat
                        Yes
                            permutations_repeat
                        No
                            permutations_no_repeat
            No
                Accomodations
                    Repeat
                        Yes
                            accomodations_repeat / accomodations(-k, n)
                        No
                            accomodations_no_repeat / accomodations(k, n)
    No
        Combinations
            Repeat
                Yes
                    combinations_repeat / combinations(-k, n)
                No
                    combinations_no_repeat / combinations(k, n)
"""


from math import factorial


def permutations_no_repeat(n):
    """
    >>> permutations_no_repeat(5)
    120

    >>> permutations_no_repeat(6)
    720
    """
    return factorial(n)


#	       n!
# ---------------------
# n1! * n2! * ... * nk!
def permutations_repeat(*counts):
    """
    >>> permutations_repeat(2, 1, 1, 1, 1, 1, 1)
    20160
    """
    if len(counts) == 0:
        return 0
    
    result, count = 1, 0

    for n in counts:
        result *= factorial(n)
        count += n

    return factorial(count) // result


#	      n!
#   ---------------
#    (n - k)! * k!
def combinations_no_repeat(k, n):
    """
    >>> combinations_no_repeat(3, 50)
    19600
    """
    return factorial(n) // (factorial(n - k) * factorial(k))


#     (n + k - 1)!
#   ---------------
#    (n - 1)! * k!
def combinations_repeat(k, n):
    """
    >>> combinations_repeat(7, 3)
    36
    """
    return factorial(n + k - 1) // (factorial(n - 1) * factorial(k))


def combinations(k, n):
    """
    >>> combinations(3, 50)
    19600
    
    >>> combinations(-7, 3)
    36
    """
    if k > 0:
        return combinations_no_repeat(k, n)

    return combinations_repeat(-k, n)


#      n!
#  ----------
#   (n - k)!
def accomodations_no_repeat(k, n):
    """
    >>> accomodations_no_repeat(3, 90)
    704880
    """
    return factorial(n) // factorial(n - k)


# n ^ k
def accomodations_repeat(k, n):
    """
    >>> accomodations_repeat(8, 62)
    218340105584896
    """
    return n ** k


def accomodations(k, n):
    """
    >>> accomodations(3, 90)
    704880
    
    >>> accomodations(-8, 62)
    218340105584896
    """
    
    if k > 0:
        return accomodations_no_repeat(k, n)
    
    return accomodations_repeat(-k, n)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
