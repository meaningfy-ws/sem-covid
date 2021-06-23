#!/usr/bin/python3

# test_python_theory.py
# Date:  17/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """


def funct_0(param1):
    """

    """


def funct_a(*args):
    """

    """
    print("This is function A")
    for a in args:
        print(a)


def funct_b(a, b, **kwargs):
    """

    """
    print("This is function B")
    print(a, b)
    print("Now the KV is printed")
    for k, v in kwargs.items():
        print(k, v)


def universal_funct(a, *args, b=None, **kwargs):
    """

    """
    print("now printing the known positional")
    print(a)
    print("now printing the arbitrary positional")
    for i in args: print(i)
    print("now printing the known kw args")
    print("b=", b)
    print("now printing the arbitrary kw args")
    for k, v in kwargs.items(): print(k, v)


def test_functs():
    funct_0(0)
    funct_0(param1=0)

    l = [0, 1, 2, 3, 4, 5, 6, 7]
    # funct_a(*l)
    m1 = {"aa": 1, "bb": 2}
    # funct_b(**m1)
    # funct_b(a=1, b=2)
    universal_funct(*l,**m1)