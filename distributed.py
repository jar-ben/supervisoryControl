from z3 import *
import itertools

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

class Distributed:
    def __init__(self, automata = []):
        self.automata = automata
        self.solver = Solver()

    def addAutomaton(self, a):
        self.automata.append(a)

    def stateVars(self, state, V):
        assert len(state) == len(self.automata)
        variables = []
        for i in range(len(state)):
            variables.append(V[i][state[i]])

        return variables

    # returns a list of controllable successor states of the state
    def succC(self, state):
        states = []

        return states

    # returns a list of uncontrollable successor states of the state
    def succUC(self, state):
        pass

    def succ(self, state):
        return self.succC(state) + self.succUC(state)

    def isMarked(self, state):
        pass

    def isSafe(self, state):
        pass

    def encode(self):
        self.X = []
        for i in range(len(self.automata)):
            self.X.append(dict((s, Bool("x_" + str(i) + "_" + s)) for s in self.automata[i].states))
        self.M = []
        for i in range(len(self.automata)):
            self.M.append(dict((s, Bool("m_" + str(i) + "_" + s)) for s in self.automata[i].states))
        self.C = []
        for i in range(len(self.automata)):
            self.C.append(dict((s, Bool("c_" + str(i) + "_" + s)) for s in self.automata[i].states))
        self.T = []
        for i in range(len(self.automata)):
            self.T.append(dict((s, Bool("t_" + str(i) + "_" + s)) for s in self.automata[i].states))

        indices = [[i for i in range(len(a.states))] for a in self.automata]
        print("indices", indices)
        self.states = list(itertools.product(*indices))
        print("combinations", self.states) 

        for s in self.states:
            left = And(self.stateVars(s, self.C)) 
            right = [And(self.stateVars(s, self.M) + self.stateVars(s, self.X))] # M[s] & X[s]
            right += [Or([And(self.stateVars(s2, self.C) + self.stateVars(s2, self.X)) for s2 in self.succ(s)])]
            solver.add(left == Or(right))

        for s in self.states:
            left = And(self.stateVars(s, self.X))
            right = [And(self.stateVars(s, self.T)), Not(And(self.stateVars(s, self.C)))]
            right += [Not(And(self.stateVars(s2, self.X))) for s2 in self.succU(s)]
            solver.add(left == Or(right))

        # marked states
        for s in self.states:
            if self.isMarked(s):
                s.add(And(self.stateVars(s, self.M)))
            else:
                s.add(Not(And(self.stateVars(s, self.M))))

        # unsafe states
        for s in self.states:
            if not self.isSafe(s):
                s.add(And(self.stateVars(s, self.T)))
            else:
                s.add(Not(And(self.stateVars(s, self.T))))

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

D = Distributed([K1, K2])
D.encode()


