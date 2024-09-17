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

def EXP(x):
    return float(np.exp(x))

def ROUND(x, digits=None, nearest=None):
    
    if nearest is None and digits is None:
        return round(x)
    
    if nearest is None:
        return round(x, digits)
    
    if nearest is not None:
        x = round(x / nearest) * nearest
        x = round(x, 10)
        return x

def DIFF(x, y):
    return abs(x - y)


def NOT(b):
    return not b


def EXACT_TO(x, digits):
    return ROUND(x, digits=digits) == x


def UNIQUE(values):
    n1 = len(values)
    n2 = len(np.unique(values))
    if n1 != n2: 
        return False
    return True

def FLOOR(x):
    import math
    return math.floor(x)


def CEIL(x):
    import math
    return math.ceil(x)


def DISTRACTORS_A(ans, n=4, step=1, seed=None):
    if seed is not None:
        np.random.seed(seed)

    k = np.random.choice(range(n+1))
    
    distractors = []
    for i in range(-k, n-k+1):
        if i == 0: continue
        d = ans + i
        distractors.append(d)

    return distractors


def DISTRACTORS(ans, n=4, p_rng=None, step=None, digits=None, seed=None):
    if seed is not None:
        np.random.seed(seed)

    # if no step is provided, determine step using p_range
    if step is None: 
        if p_rng is None: p_rng = [0.03, 0.06]
        p = np.random.uniform(p_rng[0], p_rng[1])
        step = ans*p
    
    # Determine position for correct answer
    k = np.random.choice(range(n+1))
    
    distractors = []
    for i in range(-k, n-k+1):
        if i == 0: continue
        d = ans + i * step
        if digits is not None:
            d = round(d, digits)
        distractors.append(d)

    return distractors
        
def FACT(n):
    import math
    assert(n == int(n))
    return math.factorial(int(n))

def COMBIN(n, r):
    assert(n == int(n))
    assert(r == int(r))
    return FACT(n) / FACT(r) / FACT(n - r)

def PERM(n, r):
    assert(n == int(n))
    assert(r == int(r))
    return FACT(n) / FACT(n - r) 

def MIN(values):
    return min(values)

def MAX(values):
    return max(values)


def TABLE(contents, config=None):

    default_config = {'cw':50, 'ch':20, 'sr1':True, 'sc1':True, 'align':'C'}
    if config == None: config = {}
    for k,v in default_config.items():
        if k not in config.keys():
            config[k] = v
        
    
    t = '<table style="border:1px solid black;  border-spacing:0px; border-collapse: collapse; background-color:#FFFFFF">\n'
    for i, row in enumerate(contents):
        # Determine height
        temp = config['ch']
        ch = temp[i] if type(temp) == list else temp

        # Start row
        t += f'<tr style="height:{ch}px">\n'
        
        for j, x in enumerate(row):

            # Determine Cell Color
            col = '#FFFFFF'
            if (config['sr1'] and i == 0) or (config['sc1'] and j == 0):
                col = '#E0E0E0'
                x = f'<b>{x}</b>'

            # Determine width
            temp = config['cw']
            cw = temp[j] if type(temp) == list else temp
            
            # Alignment
            temp = config['align']
            align = temp[j] if type(temp) == list else temp
            a = {'C':'center', 'L':'left', 'R':'right'}[align]
                
            t += f'<td  style="border:1px solid black; background-color:{col}; '
            t += f'width:{cw}px; text-align:{a}">'
            t += f'{x}</td>\n'

        t += '</tr>\n'
    t += '</table>\n'
    
    return t

if __name__ == '__main__':
    #print(RANGE(10, 150, 5))
    #print(ROUND(36.5, 5))
    #print(EXACT_TO(3.47, 0.1))
    #print(not EXACT_TO(3.47, 0.1))
    
    #print(UNIQUE([2, 3, 4]))
    #print(UNIQUE([2, 3, 4.01, 4 + 1/100]))
    
    print(MIN([5, 7, 10]))
    
    