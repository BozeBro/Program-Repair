import z3
import traceback
from inspect import currentframe, signature
from dataclasses import dataclass

"""
This file implements a concolic execution engine. It assumes that
a program under test is instrumented and will use the API
concolic.guard() to collect path constraints, and the API
concolic.set() and concolic.set() to manipulate a symbolic store.

The main algorithm in this file is from the DART paper:
    Patrice Godefroid, Nils Klarlund, and Koushik Sen. 2005.
    DART: Directed Automated Random Testing. In Proceedings of
    the 2005 ACM SIGPLAN conference on Programming Language
    Design and Implementation (PLDI '05).
    DOI: https://doi.org/10.1145/1065010.1065036

The entry point to the engine is concolic.run().
"""


@dataclass
class PathRecord:
    line: int
    done: bool


class ConcolicException(Exception):
    pass


# Globals
symbols = None
store = None
current_path = None
path_record = None
solver = None


def init(vars):
    global path_record, symbols
    symbols = {v: z3.Int(v) for v in vars}
    path_record = []
    reset()


def reset():
    global store, current_path, solver
    store = {v: symbols[v] for v in symbols.keys()}
    current_path = []
    solver = z3.Solver()


def get(x):
    """Get concolic store mapping of var `x`"""
    if store is not None:
        return store[x]
    else:
        return 0


def set(x, a):
    """Set concolic store mapping of var `x` to arithmetic expression `a`"""
    if store is not None:
        store[x] = a


def guard(g, line):
    """Add `g` to current path constraint"""
    if solver is None:
        return  # Concolic testing is not running

    solver.append(g)
    assert solver.check()

    # Get line number of guard
    # line = int(currentframe().f_back.f_lineno)

    # We are just seeing the k-th branch in this execution
    k = len(current_path)

    # Append to current path
    current_path.append(g)

    # Check if we have an expected k-th branch in the path record else add to it
    if k < len(path_record):
        if k == len(path_record) - 1:
            # We just got to the last negated guard
            if path_record[k].line == line:
                pass
                # We got to an unexpected branch
                raise ConcolicException(
                    (
                        "Unsoundness! Current path is %s and I'm back on line %d, "
                        + "but I was expecting to have negated this branch"
                    )
                    % (current_path, line)
                )
            else:
                path_record[k].line = line
                path_record[k].done = True
        elif path_record[k].line != line:
            # We got to an unexpected branch
            raise ConcolicException(
                (
                    "Unsoundness! Current path is %s and I'm on line %d, "
                    + "but I was expecting to go to line %d."
                )
                % (current_path, line, path_record[k].line)
            )
        # else: do nothing, we saw an expected branch
    else:
        path_record.append(PathRecord(line, False))  # Set `done`=False initially


def dump_path():
    """print Z3 constraints in Python in short hand"""
    if solver is not None:
        print(solver)


def dump_smt():
    """print Z3 constraints in Python in SMT-LIB format"""
    if solver is not None:
        print(solver.to_smt2())
def cmp(output, expected):
    if not isinstance(output, z3.ArrayRef):
        return output == expected
    cond = True
    for i, v in enumerate(expected):
        cond = z3.And(z3.Select(output, i) == v,  cond)
    return cond
import random
# Top-level runner
def sym_run(func, vars, expected, **kwargs):
    """Concolically executes `func` with parameters `vars` and returns (total_paths:int, bug_found:bool)"""
    global store, current_path, path_record, solver
    # Initialize state
    inputs = {str(v): 0 for v in vars}  # Could also be random
    init(vars)


    total_runs = 0
    bug_found = False
    constraints = None
    # f = z3.Function(z3.IntSort(), z3.IntSort(), z3.IntSort())

    while True:
        output = None
        # Run concolically
        try:
            # print("Running with inputs %s" % inputs)
            total_runs += 1
            if kwargs:
                output = func(inputs, **kwargs)
            else:
                func(inputs)
        
        except AssertionError as e:
            traceback.print_exc()
            # print("*** Assertion violation found! Inputs are: %s" % inputs)
            bug_found = True
        except ZeroDivisionError as e:
            output = ZeroDivisionError
        except IndexError:
            output = IndexError
        finally:
            # print("... Path collected: %s" % current_path)
            pc = None
            if output != None:
                pc = None
                for cond in current_path:
                    if pc == None:
                        pc = cond
                    else:
                        pc = z3.And(pc, cond)
            if pc == None and constraints == None:
                constraints = cmp(output, expected)
            elif pc == None and constraints != None:
                constraints = z3.Or(constraints, cmp(output, expected))
            elif pc != None and constraints == None:
                constraints = z3.And(pc, cmp(output, expected))
            else:
                constraints = z3.Or(constraints, z3.And(pc, cmp(output, expected)))
                
        # Figure out the next guard to negate
        next = len(current_path) - 1
        while True:
            # print(next, path_record)
            while next >= 0 and path_record[next].done:
                next = next - 1

            if next == -1:
                # print("Concolic execution complete! %d paths explored." % total_runs)
                # TODO: Actually do a random restart if there was any unsoundness observed
                # return total_runs, bug_found
                if constraints == None:
                    return False
                solver.reset()
                reset()
                return constraints
            else:
                # print("next idx=%d" % next)
                # Create a new path constraint up to `next` with the condition at index `next` negated

                current_path = current_path[:next] + [z3.Not(current_path[next])]

                path_record = path_record[: next + 1]
                solver.reset()
                solver.insert(current_path)
                # print("Path Record: %s" % path_record)
                # print(
                #     "... Negating the condition at line %d...." % path_record[-1].line
                # )
                # print("...... New candidate path: %s" % current_path)
                is_sat = solver.check()
                if is_sat == z3.sat:
                    model = solver.model()
                    inputs = {
                        var_name: model.eval(
                            var_symbol, model_completion=True
                        ).as_long()
                        for var_name, var_symbol in symbols.items()
                    }

                    # print("...... SAT! New inputs are: %s" % inputs)
                    reset()
                    # print()
                    break
                elif is_sat == z3.unsat:
                    # print("...... UNSAT!")
                    next = next - 1
                    continue  # Go look for the next branch to negate
                else:
                    raise Exception("You should not get a z3 result of %s." % is_sat)
            return