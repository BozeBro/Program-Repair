import sys 
def rankLines(lines):
    return {x : 1 for x in lines}
def main():
    nums = next(sys.stdin).split(" ")
    ranking = rankLines(nums)
    print(ranking)
main()