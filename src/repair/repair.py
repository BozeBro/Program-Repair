from interpreter import *
from fault_localization import *
from symconcolic import *
from z3 import *
import concolic
opers = {
    'mul': '*',
    'div': '/',
    'add': '+',
    'minus': '-',
    'get' : '!!',
}

def get_args(line):
    args = line.split(" ")
    return [eval(arg) for arg in args]
def get_ioPair(line):
    split = line.split(" : ")
    return tuple([get_args(split[0]), eval(split[1])])
def write_prog(prog, file='output.w3a'):
    output = ""
    with open(file, 'w') as f:

        for i in sorted(prog.keys()):
            output += f"{i}: " + " ".join(prog[i]) + '\n'
        f.write(output)
def newProg(index, pc, prog, rep):
    instr = fetch(prog, pc)
    var = instr[0]
    if index == 0:
        prog[pc] = [var, ':=', rep['__a'], opers[rep['__op']], rep['__b']]
    elif index == 1:
        prog[pc] = [var, ':=', str(rep['__d'])]
    else:
        prog[pc] = [var, ':=', str(rep['__c'])]
    return prog


def repair(testFile, outfile):
    io_pairs = None
    lines = None
    with open(testFile) as file:
        lines = file.read().splitlines()

        io_pairs = [get_ioPair(line) for line in lines[1:]]
    if io_pairs == None:
        print("File doesn't exist")
        return 1
    rank = testCoverage(lines[0], io_pairs)
    prog = getProg(lines[0])
    for pc in rank:
        try:
            C = findlines(deepcopy(prog), pc, io_pairs)
            s = Solver()
            
            for i, sol in enumerate(C):
                s.reset()
                s.add(sol)
                is_sat = s.check()
                if is_sat == sat:
                    model = s.model()
                    rep = {str(i): eval(repr(model[i])) for i in model}
                    progN = newProg(i, pc, deepcopy(prog), rep)
                    for (input, output) in io_pairs:
                        out = eval_program_dev({}, input, 1, deepcopy(progN))
                        if out != output:
                            continue
                    write_prog(progN, outfile)
                    print(f"New file created at {outfile}")
                    return
        except ZeroDivisionError:
            pass
    print("No successful New Program found")

def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print("Expecting two arguements")
        return
    repair(*args)
if __name__ == '__main__':
    main()
# repair("log.txt", "output.w3a")