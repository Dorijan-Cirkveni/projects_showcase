import src.CNF as CNF

'''An abstract solver class'''

class Solver:
    def __init__(self):
        self.CS = CNF.ClauseSet()
        return

    def findSolutions(self):
        testStack = [(self.CS, 0)]
        solutions = list()
        while len(testStack) > 0:
            CSP = testStack.pop()
            CS, depth = CSP[0], CSP[1]
            possibleliterals = {e for e in CS.literals}
            chosen = (1, None)
            for e in possibleliterals:
                le = len(CS.hasLiteral[e])
                if le > chosen[0]:
                    chosen = (le, e)
            if chosen[1] is None:
                solutions.append(CS)
                continue
            for e in [chosen[1], chosen[1].negate()]:
                CS2 = CS.copy()
                CS2.add(CNF.Clause(e))
                if not CS2.isContradictionDetected():
                    testStack.append((CS2, depth + 1))
        return solutions
