from tools.util import *

'''Implementation of basic classes required for CNF (Conjunctive Normal Form) statements.'''


class Literal(Comparable):
    def __init__(self, name, negative=False):
        self.name = name
        self.negative = negative
        return

    def __str__(self):
        return "~" * self.negative + str(self.name)

    def __hash__(self):
        return hash(str(self.name))

    def diff(self, other):
        if other is None:
            return 2
        sgn = signum(self.name, other.name)
        if sgn != 0:
            return sgn * 2
        return signum(self.negative, other.negative)

    def negate(self):
        return Literal(self.name, not self.negative)

    def base(self):
        return Literal(self.name)


class Clause(Comparable):
    '''
    A disjunction of literals.
    An empty clause indicates a contradiction ("False")
    '''

    def __init__(self, literals=None):
        if literals is None:
            literals = set()
        if type(literals) == str:
            L = literals.replace("V", "v").split("v")
            literals = set()
            for e in L:
                if e == "":
                    continue
                b = e[0] == "~"
                literals.add(Literal(e[b:], b))
        elif type(literals) == Literal:
            literals = {literals}
        self.literals = literals
        return

    def __str__(self):
        L = list(self.literals)
        L.sort()
        return "v".join(str(e) for e in L)

    def __hash__(self):
        x = 0
        for e in self.literals:
            x = x ^ hash(e)
        return x

    def __len__(self):
        return len(self.literals)

    def diff(self, other):
        if other is None:
            return -2
        sgn = signum(len(self.literals), len(other.literals))
        if sgn != 0:
            return sgn * 2
        A = list(self.literals)
        B = list(other.literals)
        A.sort()
        B.sort()
        for i in range(len(A)):
            sgn = signum(A[i], B[i])
            if sgn != 0:
                return sgn
        return 0

    def negate(self):
        return {Clause(e.negate()) for e in self.literals}

    def madeRedundantBy(self, other):
        if signum(len(self.literals), len(other.literals)) < -1:
            return False
        for e in other.literals:
            if e not in self.literals:
                return False
        return True

    def isResolveableWith(self, other):
        k = 0
        for e in self.literals:
            if e.negate() in other.literals:
                k += 1
                if k > 1:
                    return False
        return k == 1

    def resolveWith(self, other):
        L = set()
        negated = None
        for e in self:
            if e.negate() in other:
                if negated != None:
                    return None
                negated = e.negate()
            else:
                L.add(e)
        if negated == None:
            return None
        L |= {e for e in other if e != negated}
        return Clause(L)

    def __contains__(self, literal):
        return literal in self.literals

    def __iter__(self):
        return iter(self.literals)
    # ----------------END----------------


class ClauseSet(Comparable):
    '''
    A conjunction of clauses.
    '''

    def __init__(self, clauses=None):
        if clauses is None:
            clauses = set()
        self.clauses = set()
        self.literals = set()
        self.hasLiteral = dict()
        for e in clauses:
            if type(e) == Clause:
                self.add(e)
            else:
                self.add(Clause(e))
        return

    def diff(self, other):
        sig = other.isContradictionDetected() - self.isContradictionDetected()
        if sig != 0:
            return 3 * sig
        sig = signum(len(self.literals), len(other.literals))
        if sig != 0:
            return 2 * sig
        sig = signum(len(self.clauses), len(other.clauses))
        if sig != 0:
            return sig
        return 0

    def copy(self):
        X = ClauseSet()
        X.clauses = self.clauses.copy()
        X.literals = self.literals.copy()
        for e in self.hasLiteral:
            X.hasLiteral[e] = self.hasLiteral[e].copy()
        return X

    # Getters
    def __str__(self):
        L = list(self.clauses)
        L.sort()
        return ",".join([str(e) for e in L])

    def getPossibleLiterals(self):
        return self.literals | {e.negate() for e in self.literals}

    def printClauses(self):
        return {str(e) for e in self.clauses}

    def isContradictionDetected(self):
        return Clause() in self.clauses

    def isResolvedFor(self, literal):
        return Clause(literal) in self.clauses or Clause(literal.negate()) in self.clauses

    def positiveResolvedLiterals(self):
        bases = {e.base() for e in self.getPossibleLiterals()}
        return {e for e in bases if Clause(e) in self.clauses}

    def clausesSortedBy(self, Key=lambda x: len(x)):
        return sorted(self.clauses, key=Key)

    # Functions
    def remove(self, clause):
        if clause not in self.clauses:
            return
        for e in clause.literals:
            self.hasLiteral[e].remove(clause)
        self.clauses.remove(clause)
        return

    def add(self, clause):
        newLiteralSet = set()
        for e in clause.literals:
            if Clause(e) in self.clauses:
                return -1
            elif Clause(e.negate()) not in self.clauses:
                newLiteralSet.add(e)
        clause = Clause(newLiteralSet)
        for e in self.clauses:
            if clause.madeRedundantBy(e):
                return -2
        for e in clause.literals:
            if e not in self.hasLiteral:
                self.hasLiteral[e] = set()
            self.hasLiteral[e].add(clause)
            e2 = e.negate()
            if e2 not in self.hasLiteral:
                self.hasLiteral[e2] = set()
            self.literals.add(e.base())
        for e in clause.literals:
            X = set()
            for f in self.hasLiteral[e]:
                if f.madeRedundantBy(clause):
                    X.add(f)
            [self.remove(f) for f in X]
        self.clauses.add(clause)
        if len(clause) == 1:
            self.resolveForAtom(min(clause.literals))
        return 0

    def processContradiction(self):
        self.clauses = {Clause()}
        self.literals = set()
        self.hasLiteral = dict()
        return

    def resolveForAtom(self, literal):
        redundant = self.hasLiteral[literal]
        resolveable = self.hasLiteral[literal.negate()]
        X = {e for e in redundant if len(e) > 1}
        for e in X:
            self.remove(e)
        Y = {e for e in resolveable}
        for e in Y:
            f = e.resolveWith(Clause(literal))
            if f == None:
                continue
            self.remove(e)
            self.add(f)
        return

    def resolveForAtoms(self):
        localset = self.getPossibleLiterals()
        for e in localset:
            self.resolveForAtom(e)
        return

    def removeRedundant(self):
        for e in self.literals | {e0.negate() for e0 in self.literals}:
            L = list(self.hasLiteral[e])
            L.sort()
            R = set()
            for i in range(len(L)):
                for j in range(i):
                    if L[i].madeRedundantBy(L[j]):
                        R.add(L[i])
                        break
            for f in R:
                self.remove(f)
            L = None
        return

    def resolve(self):
        if self.isContradictionDetected():
            self.processContradiction()
            return True
        resolved = set()
        while True:
            done = True
            new = set()
            bases = {e.base() for e in self.literals}
            for el in bases:
                X = self.hasLiteral[el]
                Y = self.hasLiteral[el.negate()]
                for e in X:
                    for f in Y:
                        if (e, f) in resolved:
                            continue
                        resolved.add((e, f))
                        res = e.resolveWith(f)
                        if res is not None:
                            new.add(res)
                            break
                    if len(new) > 0:
                        break
                for e in new:
                    x = self.add(e)
                    if x >= 0:
                        done = False
                    if Clause() in self.clauses:
                        return self.processContradiction()
            if done:
                return False

    def prove(self, otherSet):
        for e in otherSet:
            tempSet = self.copy()
            for f in e.negate():
                tempSet.add(f)
            if tempSet.isContradictionDetected():
                continue
            tempSet.resolve()
            if not tempSet.isContradictionDetected():
                return False
        return True


def main():
    XS = ClauseSet()
    L = {"AvB", "~AvC", "~BvC"}
    for e in L:
        XS.add(Clause(e))
    print(XS.printClauses())
    XS.resolve()
    print(XS.printClauses())
    return


if __name__ == "__main__":
    main()
