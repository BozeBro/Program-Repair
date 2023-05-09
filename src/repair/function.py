from z3 import * 
from itertools import *
from util import *
# Makes a constraint that v := a + b
# where a and b are variables 
def forma(env, output):
    ops = [mul, div, minus, add]
    vars = {
        k: Int(str(k)) for k in env
    }
    # constraint = None
    # for v in vars.values():
    #     if constraint == None:
    #         constraint = expr == v
    #     else:
    #         constraint = Or(constraint, expr == v)
    constraint = False
    A = String('__a')
    B = String('__b')

    # for k, v in env.items():
    #     option = And(C == k, v == output)
    #     constraint = Or(option, constraint)
    # constraint = Or(constraint, D == output)
    

    op = String("__op")
    for (token_op, a, b) in product(ops, vars.keys(), vars.keys()):
        if type(env[a]) == int and type(env[b]) == int:
            option = And(A == a, B == b, op == token_op.__name__)
            option = And(token_op(env[a],env[b]) == output, option)
            constraint = Or(constraint, option)
    for a,b in product(vars.keys(), vars.keys()):
        envb = env[b]
        enva = env[a]
        if type(enva) == list and type(envb) == int:
            option = And(A == a, B == b, op == 'get', envb < len(enva))
            if (envb < len(enva)):
                option = And(enva[envb] == output, option)
                constraint = Or(constraint, option)
        
    # for k, v in env.items():
    #     constraint = And(constraint, vars[k] == v)
    return constraint
# Makes a constraint that v := a
def formb(env, output):
    D = Int('__d')
    if type(output) == list:
        D = Array('__dArr', IntSort(), IntSort())
        return cmp(D, output)
    return output == D
# makes constraint taht v := c where c is a constant. 
def formc(env, output):
    C = String('__c')
    vars = {
        k: Int(str(k)) for k in env
    }
    constraint = False
    for k, v in env.items():
        if (type(v) == type(output)):
            option = And(C == k, cmp(v, output))
            constraint = Or(option, constraint)
    return constraint

    
