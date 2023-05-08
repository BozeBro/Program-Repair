import sys
import z3
from interpreter import *
from itertools import *
from collections import defaultdict
from util import *
import concolic as c
from copy import deepcopy
from function import forma, formb, formc 
def transformProg(pro, i):
    ind = '_' + i
    prog = deepcopy(pro)
    for k, instr in prog.items():
        match getToken(instr):
            case 'constArrayAssign':
                [a, b, c, d] = instr
                prog[k] = [a + ind, b, c, d]
            case 'varArrayAssign':
                [a, b, c, d] = instr
                prog[k] = [a + ind, b, c, d + ind]
            case 'varAssign':
                [a, b, c] = instr
                prog[k] = [a + ind, b, c + ind]
            case 'constAssign':
                [a, b, c] = instr
                prog[k] = [a + ind, b, c]
            case 'opAssign':
                [a,b,c, d,e] = instr
                prog[k] = [a + ind, b, c + ind, d, e + ind]
            case 'len':
                [a,b,c,d] = instr
                prog[k] = [a + ind, b, c, d + ind]
            case 'print':
                [a,b] = instr 
                prog[k] = [a, b + ind]
            case 'input':
                [a, b, c, d] = instr
                prog[k] = [a + ind, b, c, d]
            case 'update':
                [a,b,c,d] = instr
                prog[k] = [a, b + ind, c + ind, d + ind]
            case 'if':
                prog[k][1] += ind
            case 'fail':
                pass
            case 'other':
                raise Exception("Not Implemented")
    return prog

def symconcolic(inputs, env, prog, args, ind, pc: int, maxcount=50):
    count = defaultdict(int)
    env = deepcopy(env)
    prog = deepcopy(prog)
    # Assign concrete value
    # Assign an arbitrary value for symbolic
    # initialize known values for concolic
    for k,v in env.items():
        c.set(k, v)
    for k, v in env.items():
        if type(v) == list:
            arr = z3.Array(f"{k}{ind}", z3.IntSort(), z3.IntSort())
            for ind, value in enumerate(v):
                arr = z3.Store(arr, ind, value)
            c.set(k, arr)
    instr = fetch(prog, pc)
    match getToken(instr):
        case 'constAssign' | 'varAssign' | 'opAssign':
            var = instr[0]
            if inputs:
                prog[pc] = [var, ":=", str(inputs[var])]
            instr = fetch(prog, pc)
            pc = eval_insn(env, args, pc, instr)
            c.set(var, z3.Int(var))
    # General case
    while 0 <= pc <= max(prog.keys()):
        instr = fetch(prog, pc)
        old_pc = pc
        count[old_pc] += 1
        if count[old_pc] >= maxcount:
            return None
        match getToken(instr):
            case 'print':
                pc += 1
                return c.get(instr[1])
            case 'len':
                c.set(instr[0], env[instr[-1]])
            case 'input':
                raise Exception("Should be passed getting inputs")
            case 'halt':
                pass
            case 'constAssign':
                c.set(instr[0] , int(instr[2]))
            case 'varAssign':
                c.set(instr[0] , c.get(instr[2]))
            case 'constArrayAssign':
                length = int(instr[3])
                # c.set(instr[0], z3.IntVector(instr[0], length))
                arr = z3.Array(instr[0], z3.IntSort(), z3.IntSort())
                for i in range(length):
                    arr = z3.Store(arr, i, 0)
                c.set(instr[0] , arr)
            case 'varArrayAssign':
                length = env[instr[3]]
                arr = z3.Array(instr[0], z3.IntSort(), z3.IntSort())
                for i in range(length):
                    arr = z3.Store(arr, i, 0)
                c.set(instr[0], arr)
            case 'goto':
                pass
            case 'if':
                lhs = instr[1]
                op = cmps[instr[2]]
                sym_lhs = c.get(lhs)
                val = env[lhs]
                cond = op(sym_lhs, 0)
                if op(val, 0):
                    c.guard(cond, 2*old_pc)
                else:
                    c.guard(z3.Not(cond), 2*old_pc+1)
            case 'print':
                pass
            case 'update':
                arr = c.get(instr[1])
                index = c.get(instr[2])
                val = c.get(instr[3])
                varr = env[instr[1]]
                vind = env[instr[2]]
                if vind >= len(varr):
                    c.guard(index == vind, old_pc * 2 + 1)
                c.set(instr[1], z3.Store(arr, index, val))
            case 'opAssign':
                [lhs, _, v0, op, v1] = instr
                sv0 = c.get(v0)
                sv1 = c.get(v1)
                if op == '/':
                    if env[v1] == 0:
                        c.guard(sv1 == 0, old_pc * 2 + 1)
                    if isinstance(sv0, z3.ArithRef) or isinstance(sv1, z3.ArithRef):
                        c.set(lhs, sv0 / sv1)
                    else:
                        c.set(lhs, ops[op](sv0, sv1))
                elif op == '!!':
                    var0 = env[v0]
                    var1 = env[v1]
                    if var1 >= len(var0):
                        c.guard(sv1 == var1, old_pc *2 + 1)
                    c.set(lhs, z3.Select(sv0, sv1))
                else:
                    c.set(lhs, ops[op](sv0, sv1))
        pc = eval_insn(env, args, pc, instr)


def formula(env, expr, output):
    ops = [mul, div, minus, add]
    vars = {
        k: z3.Int(k) for k in env
    }
    initC = True
    # for k, v in env.items():
    #     initC = z3.And(initC, vars[k] == v)
    constraint = False
    for v in vars.values():
        constraint = z3.Or(constraint, expr == v)
    # constraint = z3.Or(constraint, expr == z3.IntSort())
    for op, (left, right) in product(ops, permutations(list(vars.values()) + list(vars.values()), 2)):
        option = expr == op(left, right)
        constraint = z3.Or(constraint, option)
    return z3.And(initC, constraint) 
def findline(ind, prog, args, line,expected):
    env = {}
    pc = 1
    prog = transformProg(prog, ind)
    while 0 <= pc <= max(prog) and pc != line:
        instr = fetch(prog, pc)
        if instr[0] == "print":
            pc += 1
            continue
        pc = eval_insn(env, args, pc, instr)
    if pc != line:
        return [True, True, True, True]
        # raise Exception("pc counter is out of bounds or ended too early")
    old_env = env.copy()
    instr = fetch(prog, pc)
    kwargs = {
        "env": old_env.copy(),
        "prog": prog.copy(),
        "pc": pc,
        "args": args,
        "ind": str(ind)
    }
    c.init([instr[0]])
    constraints = c.sym_run(symconcolic, [instr[0]], expected,**kwargs)
    # constraints = z3.And(constraints, z3.Int(instr[0]) == z3.Int("__res__"))
    s = z3.Solver()
    s.add(constraints)
    is_sat = s.check()
    new_env = {}
    for k, v in old_env.items():
        new_k = k.find("_")
        new_k = k[:new_k]
        new_env[new_k] = v
    rep = None
    if is_sat == z3.sat:
        model = s.model()
        if len(model) > 0:
            # m = model["__res__"]
            rep = {str(i): eval(repr(model[i])) for i in model}
            rep = [eval(repr(model[i])) for i in model][0]
        
    funcs = [forma, formb, formc]
    return [z3.And(constraints, f(new_env, rep)) for f in funcs]

def findlines(prog, line, io_pairs):
    constraint = []
    for i, (args, expected) in enumerate(io_pairs):
        if constraint != []:
            con =  findline(str(i), prog, args,line, expected)
            for i in range(len(con)):
                constraint[i] = z3.And(con[i], constraint[i])
        else:
            constraint = findline(str(i), prog, args, line, expected)
    return constraint


def main():
    # c.init([])
    args = sys.argv[1:]
    if args == []:
        print("No input file given")
        return 1
    m = [(getProg(args[0]), int(args[1]), 1)]
    C = findlines(m)
    z3.solve(C)
                
if __name__ == '__main__':
    main()