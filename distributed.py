from z3 import *


class Automaton:
    def __init__(self, init):
        self.init = init
        self.states = set()
        self.transitions = dict()
        self.marked = set()

    def addTransition(self, q1, q2, controllable = True, action = ""):
        self.states.add(q1)
        self.states.add(q2)
        if not q1 in self.transitions:
            self.transitions[q1] = []
        self.transitions[q1].append((q2, action, controllable))

    def markState(self, q):
        if q not in self.states:
            print("The state {} is unknown. Add transitions before marking states.".format(q))
        assert q in self.states
        self.marked.add(q)

#######################
### Definition of the base automata
#######################

### Example 1

#Automaton K1
K1 = Automaton("q0")
K1.addTransition("q0", "q1", controllable = True, action = "alpha")
K1.addTransition("q1", "q2", controllable = False, action = "beta")
K1.addTransition("q1", "q2", controllable = False, action = "theta")
K1.addTransition("q2", "q0", controllable = True, action = "alpha")
K1.addTransition("q1", "q3", controllable = True, action = "a")
K1.addTransition("q3", "q4", controllable = False, action = "b")
K1.addTransition("q4", "q3", controllable = False, action = "c")
K1.addTransition("q4", "q5", controllable = False, action = "beta")
K1.addTransition("q5", "q0", controllable = True, action = "alpha")
K1.markState("q2")
K1.markState("q5")

#Automaton K2
K2 = Automaton("p0")
K2.addTransition("p0", "p1", controllable = True, action = "alpha")
K2.addTransition("p1", "p2", controllable = False, action = "beta")
K2.addTransition("p1", "p2", controllable = False, action = "theta")
K2.addTransition("p2", "p0", controllable = True, action = "alpha")
K2.addTransition("p1", "p3", controllable = True, action = "f")
K2.addTransition("p3", "p4", controllable = False, action = "g")
K2.addTransition("p4", "p3", controllable = False, action = "h")
K2.addTransition("p4", "p5", controllable = False, action = "theta")
K2.addTransition("p5", "p0", controllable = True, action = "alpha")
K2.markState("p2")
K2.markState("p5")




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
    solver.add(C[s] == Or([M[s]] + [C[s2] for s2 in (transitionsC[s] + transitionsU[s])]))

for s in states:
    solver.add(Not(X[s]) == Or([T[s], Not(C[s])] + [Not(X[s2]) for s2 in transitionsU[s]]))

print(solver)

#assumptions (fixed variables)
assumptions = []
for s in states:
    assumptions.append(M[s] if marked[s] else Not(M[s]))
    assumptions.append(T[s] if unsafe[s] else Not(T[s]))


#if not solver.check(assumptions + [C["q5"]]):
if  solver.check(assumptions) == unsat:
    print("UNSAT")
else:
    print("SAT")
    m = solver.model()
    for s in states:
        print(s, m[X[s]])


solver.add(Not(X["q0"]))
if solver.check(assumptions) == unsat:
    print("UNSAT")
else:
    print("SAT")
    m = solver.model()
    for s in states:
        print("x" + s[1:], m[X[s]])
    for s in states:
        print("m" + s[1:], m[M[s]])
    for s in states:
        print("t" + s[1:], m[T[s]])
    for s in states:
        print("c" + s[1:], m[C[s]])
#count the number of models
models = []









