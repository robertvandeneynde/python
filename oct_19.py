#! /usr/bin/env python3
# coding: utf-8
def sum_of_datetime_intervals(x:str) -> 'timedelta':
    """
    >>> sum_of_datetime_intervals('09:30-12:10 14:30-16:30')
    datetime.timedelta(seconds=16800)
    """
    from datetime import date, time, datetime
    x = x.replace('-', ' ')
    N = datetime.now()
    x = [x  #datetime.combine(N, b) - datetime.combine(N, a)
         for x in x.split()
         for x in [ list(map(int, x.split(':'))) ]
         for t in [ time(*x) ] ]
    x = [time(*x) for x in x]
    todt = lambda x: datetime.combine(N, x) 
    x = [todt(x[i+1]) - todt(x[i]) for i in range(0, len(x), 2)]
    from functools import reduce, partial
    reducesum = partial(reduce, lambda x,y:x+y)
    return reducesum(x)
    
