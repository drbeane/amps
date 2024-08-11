import numpy as np

def RANGE(start, stop, step, exclude=None):
    while True:
        rng = np.arange(start, stop+step, step)
        x = np.random.choice(rng)
        x = round(x, 10)
        if exclude is None:
            return x
        if x not in exclude:
            return x

def ROUND(x, nearest):
    #print(x / nearest)
    x = round(x / nearest) * nearest
    x = round(x, 10)
    return x

def DIFF(x, y):
    return abs(x - y)

def NOT(b):
    return not b

def EXACT_TO(x, prec):
    return ROUND(x, prec) == x



if __name__ == '__main__':
    print(RANGE(10, 150, 5))
    print(ROUND(36.5, 5))
    print(EXACT_TO(3.47, 0.1))
    print(not EXACT_TO(3.47, 0.1))