import z3
def getProg(file):
    prog = {}
    with open(file) as f:
        for line in f.readlines():
            lineno, instr = line.split(": ")
            prog[int(lineno)] = instr.strip().split(" ")
    return prog

def mul(x1, x2):
    return x1 * x2

def div(x1, x2):
    if x2 == 0:
        return None
    return x1 // x2

def minus(x1, x2):
    return x1 - x2

def add(x1, x2):
    return x1 + x2
def cmp(output, expected):
    if not isinstance(output, z3.ArrayRef):
        return output == expected
    cond = True
    for i, v in enumerate(expected):
        cond = z3.And(z3.Select(output, i) == v,  cond)
    return cond