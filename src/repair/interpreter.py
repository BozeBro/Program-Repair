from typing import *
import sys

def getProg(file):
    prog = {}
    with open(file) as f:
        for line in f.readlines():
            lineno, instr = line.split(": ")
            prog[int(lineno)] = instr.strip().split(" ")
    return prog

ops = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x // y,
    '!!': lambda x, y: x[y]
}
cmps = {
    '<': lambda x, y: x < y,
    '=': lambda x, y: x == y
}
def getToken(instr):
    if instr[0] == 'halt':
        return 'halt'
    match [instr[0], instr[1]]:
        case [x, ":="]:
            if len(instr) == 3:
                v = instr[2]
                if v.isnumeric():
                    return 'constAssign'
                return 'varAssign'
            elif instr[2] == 'array':
                v = instr[3]
                if v.isnumeric():
                    return 'constArrayAssign'
                return 'varArrayAssign'
            return 'opAssign'
        case ['goto', _]:
            return 'goto'
        case ['if', _]:
            return 'if'
        case ['print', _]:
            return 'print'
        case ['update', _]:
            return 'update'
        case other:
            return 'fail'
    
# getProg("fun_progs/selection_sort.w3a", prog)
def eval_insn(env, pc : int, instr : List[str]) -> int:
    global ops, cmps
    def update(env, id, value):
        env[id] = value
    match getToken(instr):
        case 'halt':
            return -1
        case 'constAssign':
            v = instr[2]
            update(env, instr[0], int(v))
            return pc + 1
        case 'varAssign':
            v = env[instr[2]]
            update(env, instr[0], v)
            return pc + 1
        case 'constArrayAssign':
            v = instr[3]
            update(env, instr[0], [0 for _ in range(int(v))])
            return pc + 1
        case 'varArrayAssign':
            v = env[instr[3]]
            update(env, instr[0], [0 for _ in range(v)])
            return pc + 1
        case 'goto':
            return int(instr[1])
        case 'if':
            lhs = instr[1]
            op = cmps[instr[2]]
            line = instr[5]
            v = env[lhs]
            if op(v, 0):
                return int(line)
            return pc + 1
        case 'print':
            print(env[instr[1]])
            return pc + 1
        case 'update':
            arrName = instr[1]
            index = env[instr[2]]
            val = env[instr[3]]
            arr = env[arrName]
            arr[index] = val
            return pc + 1
        case 'opAssign':
            [lhs, _, v0, op, v1] = instr
            v0 = env[v0]
            v1 = env[v1]
            update(env, lhs, ops[op](v0, v1))
            return pc + 1

        case 'fail':
            raise Exception("Instruction not implemented")

def fetch(listing, location):
    if location not in listing:
        raise Exception(f"No instruction at {location}")
    return listing[location]
def eval_program(env, pc, listing):
    while pc != -1:
        instr = fetch(listing, pc)
        pc = eval_insn(env, pc, instr)
        # print(instr, pc)
        if pc > max(listing):
            raise Exception(f"Illegal line number {pc}")
# eval_program(env, 1, prog)

def main():
    env = {}
    args = sys.argv[1:]
    if args == []:
        print("No input file given")
        return 1
    prog = getProg(args[0])
    eval_program(env, 1, prog)

if __name__ == '__main__':
    main()
    
