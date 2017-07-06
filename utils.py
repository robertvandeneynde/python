def bytes2human(n, format="{value}{symbol}"):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('B','K','M','G','T','P','E','Z','Y')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format.format(value=str(value)[:4], symbol=symbol) #locals()
    return format.format(symbol=symbols[0], value=n)
