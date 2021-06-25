from z3 import *


#######################
### Definition of the automaton
#######################
states = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"]
transitionsC = dict((s, []) for s in states) #controllable transitions
transitionsC["q0"] = ["q6", "q9"]
transitionsC["q1"] = ["q3"]
transitionsC["q3"] = ["q4"]
transitionsC["q6"] = ["q7"]
transitionsC["q7"] = ["q3"]

transitionsU = dict((s, []) for s in states) #uncontrollable transitions
transitionsU["q0"] = ["q1"]
transitionsU["q1"] = ["q2"]
transitionsU["q2"] = ["q1"]
transitionsU["q3"] = ["q0"]
transitionsU["q4"] = ["q5"]
transitionsU["q6"] = ["q8"]
transitionsU["q9"] = ["q10"]
transitionsU["q10"] = ["q9"]


toMark = ["q3", "q4"]
marked = dict((s, s in toMark) for s in states) #binary clasifier for marked states

toMarkUnsafe = ["q5", "q8"]
unsafe = dict((s, s in toMarkUnsafe) for s in states) #binary clasifier for unsafe states


#######################
### Z3 Boolean encoding
#######################
#build the variables
X = dict((s, Bool("x" + s)) for s in states)
M = dict((s, Bool("m" + s)) for s in states)
C = dict((s, Bool("c" + s)) for s in states)
D = dict()
T = dict((s, Bool("T" + s)) for s in states) #unsafe state variables

#note that we assume here that there are not two states q1, q2 such that there is both a controllable and uncontrollable transition q1->q2
for q1 in states:
    for q2 in (transitionsC[q1] + transitionsU[q1]):
        D[(q1,q2)] = Bool(q1 + q2)


#feed the formulas to the solver
solver = Solver()

for s in states:
    solver.add(C[s] == Or(And(M[s],X[s]), Or([And(C[s2],X[s2]) for s2 in (transitionsC[s] + transitionsU[s])])))

for s in states:
    solver.add(Not(X[s]) == Or([T[s], Not(C[s])] + [Not(X[s2]) for s2 in transitionsU[s]]))

print(solver)

#assumptions (fixed variables)
assumptions = []
for s in states:
    assumptions.append(M[s] if marked[s] else Not(M[s]))
    assumptions.append(T[s] if unsafe[s] else Not(T[s]))


for x in range(len(states)):
    for c in range(len(states)):
        solver.push()
        pblist = []
        for s in states:
            pblist.append((X[s],1))
        solver.add(z3.PbEq(pblist, x))
        pblist = []
        for s in states:
            pblist.append((C[s],1))
        solver.add(z3.PbEq(pblist, c))

        if  solver.check(assumptions) == unsat:
            print("UNSAT for ", x, c)
        else:
            print("SAT for ", x, c)
            m = solver.model()
            for s in states:
                print(s, m[X[s]])
        solver.pop()
