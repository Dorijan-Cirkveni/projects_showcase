import src.CNF as CNF
from src.solver import Solver

'''Sudoku solver'''


def SudokuLiteral(row, column, value, negative=False):
    return CNF.Literal(str(row) + str(column) + str(value), negative)


def ReadSudokuLiteral(literal):
    s = literal.name
    return int(s[0]), int(s[1]), int(s[2]), literal.negative


class SudokuCS(Solver):
    def oneOfEvery(self, fields):
        size = self.size
        if len(fields) != size:
            return False
        for k in range(1, size + 1):
            cls = {SudokuLiteral(e[0], e[1], k) for e in fields}
            self.CS.add(CNF.Clause(cls))
        for i in range(size):
            for j in range(i + 1, size):
                for k in range(1, size + 1):
                    first = fields[i]
                    second = fields[j]
                    a, b = first[0], first[1]
                    c, d = second[0], second[1]
                    cl = CNF.Clause({SudokuLiteral(a, b, k, True),
                                     SudokuLiteral(c, d, k, True)})
                    self.CS.add(cl)
        return

    def __init__(self, preset=None, size=2, group=None):
        super().__init__()
        if preset is None:
            preset = dict()
        self.size = size
        for e in preset:
            sl = SudokuLiteral(e[0], e[1], preset[e])
            cl = CNF.Clause(sl)
            self.CS.add(cl)
        for i in range(size):
            for j in range(size):
                for first in range(1, size + 1):
                    for second in range(first + 1, size + 1):
                        cl = CNF.Clause({SudokuLiteral(i, j, first, True),
                                         SudokuLiteral(i, j, second, True)})
                        self.CS.add(cl)
        for i in range(size):
            self.oneOfEvery([(i, j) for j in range(size)])
            self.oneOfEvery([(j, i) for j in range(size)])
            print(i)
        if group is not None:
            b = size // group[1]
            d = size // group[1]
            X = [[list() for j in range(d)] for i in range(b)]
            for i in range(size):
                for j in range(size):
                    X[i // b][j // d].append((i, j))
            for e in X:
                for f in e:
                    self.oneOfEvery(f)
        self.size = size
        return

    def possiblevalues(self, CS=None):
        if CS == None:
            CS = self.CS
        size = self.size
        matrix = list()
        for i in range(size):
            row = list()
            for j in range(size):
                tempset = {k + 1 for k in range(size)}
                for k in range(1, size + 1):
                    if CNF.Clause(SudokuLiteral(i, j, k)) in CS.clauses:
                        tempset = {k}
                        break
                    elif CNF.Clause(SudokuLiteral(i, j, k, True)) in CS.clauses:
                        tempset.remove(k)
                row.append(tempset)
            matrix.append(row)
        return matrix

    def printsolution(self, CS=None):
        if CS is None:
            CS = self.CS
        size = self.size
        for i in range(size):
            for j in range(size):
                s = '_'
                for k in range(1, size + 1):
                    if CNF.Clause(SudokuLiteral(i, j, k)) in CS.clauses:
                        s = str(k)
                        break
                print(s, end="")
            print()
        return

    def print(self):
        matrix = self.possiblevalues()
        for e in matrix:
            for f in e:
                print(f)
            print()
        return

    def printSingleFieldClauses(self):
        size = self.size
        M = [[set() for i in range(size)] for j in range(size)]
        for clause in self.CS.clauses:
            F = None
            for literal in clause.literals:
                a, b, v, neg = ReadSudokuLiteral(literal)
                if F is None:
                    F = (a, b)
                elif F != (a, b):
                    F = (-1, -1)
            if F is not None and F[0] != -1:
                M[F[0]][F[1]].add(clause)
        for i in range(size):
            for j in range(size):
                for cl in M[i][j]:
                    for lit in cl.literals:
                        a, b, v, neg = ReadSudokuLiteral(lit)
                        print("~" * neg + str(v), end="")
                    print("", end=",")
                print()
            print()
        return

def main():
    PS = dict()
    if PS == dict():
        for i in range(9):
            S = input("Values:")
            S += "0" * 9
            for j in range(9):
                n = int(S[j])
                if n != 0:
                    PS[(i, j)] = n
    X = SudokuCS(PS, 9, [3, 3])
    X.printsolution()
    X.printSingleFieldClauses()
    input("Press to continue")
    print("Processing...")
    L = X.findSolutions()
    for e in L:
        X.printsolution(e)
    return
