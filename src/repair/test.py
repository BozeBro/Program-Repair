import concolic


# Run concolic execution and compare expected result
def test_run(name, vars, bug_expected, paths_expected):
    print("\n\n\n####### Test %s #######\n" % name)
    func = getattr(__import__(name), name)
    paths, bug = concolic.run(func, vars)
    if bug_expected == bug and paths_expected == paths:
        return 1
    else:
        return 0


# If you want to run only one test, comment out the rest of the lines
p = 0
# p += test_run("signed", ["x"], bug_expected=False, paths_expected=2)
# p += test_run("f1", ["x", "z"], bug_expected=True, paths_expected=4)
# p += test_run("f2", ["a", "b", "c"], bug_expected=True, paths_expected=5)
p += test_run("sum", ["x"], bug_expected=False, paths_expected=6)

print("--------")
print("%d tests passed." % p)
