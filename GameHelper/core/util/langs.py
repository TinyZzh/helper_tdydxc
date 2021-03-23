# -*- encoding=utf8 -*-

def is_iterable(obj):
    try:
        i = iter(obj)
        return True
    except TypeError as e:
        return False