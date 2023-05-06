import sys
import z3
from interpreter import *
import concolic as c
def symconcolic(expr, old_env, env, prog, pc):
    instr = fetch(prog, pc)
    for k,v in old_env.items():
        c.set(k, v)
    if (len(instr) > 2 and instr[1] == ':='):
        v = instr[0]
        c.set(v, z3.Int(v))
    while 0 <= pc <= max(prog):
        instr = fetch(prog, pc)
        if instr[0] == "print":
            pc += 1
            continue
        pc = eval_insn(env, pc, instr)
        match getToken(instr):
            case 'halt':
                continue
            case 'constAssign':
                c.set(instr[0], int(instr[2]))
            case 'varAssign':
                c.set(instr[0], c.get(instr[2]))
            case 'constArrayAssign':
                length = int(instr[3])
                # c.set(instr[0], z3.IntVector(instr[0], length))
                arr = z3.IntVector(instr[0], length)
                for i in range(length):
                    z3.Store(arr, i, 0)
                c.set(instr[0], arr)
            case 'varArrayAssign':
                length = c.get(instr[3])
                arr = z3.IntVector(instr[0], length)
                for i in range(length):
                    z3.Store(arr, i, 0)
                c.set(instr[0], arr)
            case 'goto':
                pass
            case 'if':
                lhs = instr[1]
                op = cmps[instr[2]]
                sym_lhs = c.get(lhs)
                cond = op(sym_lhs, 0)
                if op(sym_lhs, 0):
                    c.guard(cond)
                else:
                    c.guard(z3.Not(cond))
            case 'print':
                pass
            case 'update':
                arr = c.get(instr[1])
                index = c.get(instr[2])
                val = c.get(instr[3])
                c.set(instr[1], z3.Store(arr, index, val))
            case 'opAssign':
                [lhs, _, v0, op, v1] = instr
                sv0 = c.get(v0)
                sv1 = c.get(v1)
                c.set(lhs, ops[op](sv0, sv1))
def findline(f, line):

    prog = getProg(f)
    env = {}
    pc = 1
    while 0 <= pc <= max(prog) and pc != line:
        instr = fetch(prog, pc)
        if instr[0] == "print":
            pc += 1
            continue
        pc = eval_insn(env, pc, instr)
    if pc != line:
        raise Exception("pc counter is out of bounds or ended too early")
    old_env = env.copy()
    instr = fetch(prog, pc)
    eval_insn(env, pc, instr)
    old = env[instr[0]]
    symconcolic(old_env, old_env, prog, pc)
    



def main():
    c.init([])
    args = sys.argv[1:]
    if args == []:
        print("No input file given")
        return 1
    prog = getProg(args[0])
    findline(args[0], int(args[1]))
    print(c.store)
                
if __name__ == '__main__':
    main()