import sys
import z3
from interpreter import *
import concolic as c
from copy import deepcopy
def symconcolic(inputs, env, prog, args, pc: int):
    env = deepcopy(env)
    prog = deepcopy(prog)
    # Assign concrete value
    # Assign an arbitrary value for symbolic
    # initialize known values for concolic
    for k,v in env.items():
        c.set(k, v)
    for k, v in env.items():
        if type(v) == list:
            arr = z3.Array("k", z3.IntSort(), z3.IntSort())
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

        # case 'if':
        #     prog[pc] = ["if"] + ["0"] + ["="] + ["0"] + ["goto", str(instr[-1])]
        #     pc = eval_insn(env, pc, fetch(prog, pc))
    # General case
    while 0 <= pc <= max(prog.keys()):
        # print(c.current_path, instr)
        instr = fetch(prog, pc)
        if instr[0] == "print":
            pc += 1
            return c.get(instr[1])
        old_pc = pc
        match getToken(instr):
            case 'len':
                c.set(instr[0], env[instr[-1]])
            case 'input':
                raise Exception("Should be passed getting inputs")
            case 'halt':
                pass
            case 'constAssign':
                c.set(instr[0], int(instr[2]))
            case 'varAssign':
                c.set(instr[0], c.get(instr[2]))
            case 'constArrayAssign':
                length = int(instr[3])
                # c.set(instr[0], z3.IntVector(instr[0], length))
                arr = z3.Array(instr[0], z3.IntSort(), z3.IntSort())
                for i in range(length):
                    arr = z3.Store(arr, i, 0)
                c.set(instr[0], arr)
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
                    # print(v0, type(sv0))
                    c.set(lhs, z3.Select(sv0, sv1))
                else:
                    c.set(lhs, ops[op](sv0, sv1))
        pc = eval_insn(env, args, pc, instr)
                        
def findline(f, line):

    prog = getProg(f)
    env = {}
    pc = 1
    args = [100]
    while 0 <= pc <= max(prog) and pc != line:
        instr = fetch(prog, pc)
        if instr[0] == "print":
            pc += 1
            continue
        pc = eval_insn(env, args, pc, instr)
    if pc != line:
        raise Exception("pc counter is out of bounds or ended too early")
    old_env = env.copy()
    instr = fetch(prog, pc)
    kwargs = {
        "env": old_env.copy(),
        "prog": prog.copy(),
        "pc": pc,
        "args": args
    }
    print(instr[0])
    c.init([instr[0]])
    inputs = c.sym_run(symconcolic, [instr[0]], 0,**kwargs)
    m = z3.ArraySort(z3.IntSort(), z3.IntSort())

    z3.solve(inputs)
    



def main():
    # c.init([])
    args = sys.argv[1:]
    if args == []:
        print("No input file given")
        return 1
    findline(args[0], int(args[1]))
    # print(c.store)
                
if __name__ == '__main__':
    main()