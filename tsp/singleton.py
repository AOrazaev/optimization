# -*- coding: utf-8 -*-
"""Singleton decorator for python classes.

Lets create some singleton counter:

    >>> @Singleton
    ... class Counter(object):
    ...     def __init__(self, start_from=0):
    ...         self.count = start_from
    ...     def inc(self):
    ...         self.count += 1
    ...
    >>> counter = Counter(start_from=40)
    >>> counter is Counter()
    True
    >>> isinstance(counter, Counter)
    True

Attention! Singleton does not calling __init__ after creation:

    >>> Counter(start_from=0).inc(); Counter(start_from=1000).inc()
    >>> counter.count
    42

"""

class Singleton(object):
    def __init__(self, decorated):
        self._decorated = decorated

    def __call__(self, *args, **kwargs):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated(*args, **kwargs)
            return self._instance

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
