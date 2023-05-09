import sys 
from util import getProg
from interpreter import *
from collections import defaultdict
# ranks files just like the SemFix paper. Sorted list is the return type
def rankLines(lines, sc, fl, sc_count, fl_count):
    rank = {}
    
    sus = lambda x, y, z :  (fl[x]/z)/(sc[x]/y + fl[x]/z)
    for line in lines:
        if sc[line] + fl[line] > 0:
            y = sc_count
            if y == 0:
                sc[line] = 0
                y += 1
            z = fl_count
            if z == 0:
                fl[line] = 0
                z += 1
            rank[line] = sus(line, y, z)
    return sorted(rank.keys(), key=lambda x: -1 * rank[x])
def getCoverage(prog, freq, args):
    pc = 1
    env = {}
    res = None
    while 1 <= pc <= max(prog):
        instr = fetch(prog, pc)
        track = ['constAssign', 
                 'varAssign', 
                 'constAssignArray', 
                 'varAssignArray', 
                 'opAssign']
        token = getToken(instr)
        if token in track:
            freq[pc] += 1
        elif token == 'print':
            res = env[instr[1]]
            return freq, res
        pc = eval_insn(env, args, pc, instr)


    return freq, res
# High level wrapper for the rankLines function. We get each program with the test input 
# and grab the rankings from each and coalesce them together
def testCoverage(file, argsv):
    fail = defaultdict(int)
    succ = defaultdict(int)
    succ_total = 0
    fail_total = 0
    prog = getProg(file)
    for args in argsv:
        cur_freq = defaultdict(int)

        cur_freq, ret = getCoverage(prog, cur_freq, args[0])
        if ret == args[1]:
            succ_total += 1
            for line, seen in cur_freq.items():
                succ[line] += seen
        else:
            fail_total += 1
            for line, seen in cur_freq.items():
                fail[line] += seen
    return rankLines(prog.keys(), succ, fail, succ_total, fail_total)

        




    

