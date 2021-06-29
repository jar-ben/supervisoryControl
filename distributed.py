from z3 import *
import itertools

class Automaton:
    def __init__(self, init):
        self.init = init
        self.states = []
        self.transitions = dict()
        self.marked = set()
        self.unsafe = set()
        self.alphabet = set()
        self.mapa = dict()

    def getAlphabet(self):
        if len(self.alphabet) == 0:
            for state in self.transitions:
                for t in self.transitions[state]:
                    self.alphabet.add(t[1])
        return self.alphabet

    def addTransition(self, q1, q2, controllable = True, action = ""):
        if q1 not in self.states:
            self.states.append(q1)
            self.mapa[q1] = len(self.states) - 1
        if q2 not in self.states:
            self.states.append(q2)
            self.mapa[q2] = len(self.states) - 1
        if not q1 in self.transitions:
            self.transitions[q1] = []
        self.transitions[q1].append((q2, action, controllable))

    def markState(self, q):
        if q not in self.states:
            print("The state {} is unknown. Add transitions before marking states.".format(q))
        assert q in self.states
        self.marked.add(q)

    def setUnsafe(self, q):
        if q not in self.states:
            print("The state {} is unknown. Add transitions before marking states.".format(q))
        assert q in self.states
        self.unsafe.add(q)

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
            variables.append(V[i][self.automata[i].states[state[i]]])
        return variables

    # returns a list of controllable successor states of the state
    def succC(self, state):
        states = []
        bigAlphabet = set()
        for i in range(len(self.automata)):
            bigAlphabet = bigAlphabet.union(self.automata[i].getAlphabet())

        for action in bigAlphabet:
            succ = []
            for i in range(len(state)):
                s = self.automata[i].states[state[i]]
                if action not in self.automata[i].getAlphabet(): #the state does not change
                    succ.append(state[i])
                elif s not in self.automata[i].transitions:
                    succ.append(-1) #the state is a dead end
                else:
                    enabled = False
                    for t in self.automata[i].transitions[s]:
                        if t[1] == action:
                            index = self.automata[i].mapa[t[0]]
                            succ.append(index)
                            enabled = True
                            break
                    if not enabled: #the action is not enabled in the state
                        succ.append(-1)
            if not -1 in succ:
                states.append(succ[:])

        return states

    # returns a list of uncontrollable successor states of the state
    def succUC(self, state):
        states = []
        
        return states

    def succ(self, state):
        return self.succC(state) + self.succUC(state)

    def isMarked(self, state):
        marked = True
        for i in range(len(state)):
            s = self.automata[i].states[state[i]]
            marked = marked and s in self.automata[i].marked
        return marked

    def isSafe(self, state):
        unsafe = False
        for i in range(len(state)):
            s = self.automata[i].states[state[i]]
            unsafe = unsafe or s in self.automata[i].unsafe
        return not unsafe

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
            self.solver.add(left == Or(right))

        for s in self.states:
            left = And(self.stateVars(s, self.X))
            right = [And(self.stateVars(s, self.T)), Not(And(self.stateVars(s, self.C)))]
            right += [Not(And(self.stateVars(s2, self.X))) for s2 in self.succUC(s)]
            self.solver.add(left == Or(right))

        # marked states
        for s in self.states:
            if self.isMarked(s):
                self.solver.add(And(self.stateVars(s, self.M)))
            else:
                self.solver.add(Not(And(self.stateVars(s, self.M))))

        # unsafe states
        for s in self.states:
            if not self.isSafe(s):
                self.solver.add(And(self.stateVars(s, self.T)))
            else:
                self.solver.add(Not(And(self.stateVars(s, self.T))))

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


