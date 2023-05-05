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
    '/': lambda x, y: x / y,
    '!!': lambda x, y: x[y]
}
cmps = {
    '<': lambda x, y: x < y,
    '=': lambda x, y: x == y
}
# getProg("fun_progs/selection_sort.w3a", prog)
def eval_insn(env, pc : int, instr : List[str]) -> int:
    global ops, cmps
    def update(env, id, value):
        env[id] = value
    if instr[0] == 'halt':
        return -1
    match [instr[0], instr[1]]:
        case [x, ":="]:
            # ConstAssign, VarAssign
            if len(instr) == 3:
                # x := a
                # ConstAssign
                v = instr[2]
                if v.isnumeric():
                    update(env, x, int(v))
                else:
                    update(env, x, env[v])
                return pc + 1
            # Array assigns
            elif instr[2] == 'array':
                v = instr[3]
                if v.isnumeric():
                    update(env, x, [0 for _ in range(int(v))])
                else:
                    update(env, x, [0 for _ in range(env[v])])
                return pc + 1
            # OpAssign x := v0 op v1 
            else:
                v0 = env[instr[2]]
                v1 = env[instr[4]]
                op = ops[instr[3]]
                update(env, x, op(v0, v1))
                return pc + 1
        case ["goto", x]:
            return int(x)
        case ["if", _]:
            lhs = instr[1]
            op = cmps[instr[2]]
            line = instr[5]
            v = env[lhs]
            if op(v, 0):
                return int(line)
            return pc + 1
        case ["print", x]:
            print(env[x])
            return pc + 1
        case ["update", arrName]:
            index = env[instr[2]]
            val = env[instr[3]]
            arr = env[arrName]
            arr[index] = val
            return pc + 1
        case other:
            raise Exception("Instruction not Implemented")
def fetch(listing, location):
    if location not in listing:
        raise Exception(f"No instruction at {location}")
    return listing[location]
def eval_program(env, pc, listing):
    while pc != -1:
        instr = fetch(listing, pc)
        pc = eval_insn(env, pc, instr)
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
    
