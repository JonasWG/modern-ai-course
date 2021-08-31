# pacmanAgents.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from pacman import Directions
from game import Agent
import copy
import random
import game
import util
import collections

class BaseAgent(game.Agent):
    class State:
        def __init__(self):
            self.actions = ['GoRight','GoLeft','GoForward','GoBack']

    def registerInitialState(self, state):
        """AgentState is stored in state"""
        self._dir = 0
        self._dirsMap = {(1,0):'East',(0,-1):'South',(-1,0):'West',(0,1):'North'}
        self._dirs = [(1,0),(0,-1),(-1,0),(0,1)]
        self._percept = ('clear', None)
        self._actions = ['GoRight','GoLeft','GoForward','GoBack']
        self._state = self.State()
        
    def getAction(self, state):
        """Get the next action. Note that the state passed here is used only
        to identify legal actions."""
        self._state = self.update_state_with_percept(self._percept, self._state)
        action = self.choose_action(copy.deepcopy(self._state))
        self._state = self.update_state_with_action(action, self._state)

        # Map the action
        do = self.mapAction(action)
        # If bump
        if do not in state.getLegalPacmanActions() and do != "Nothing":
            self._percept = ('clear','bump')
        else:
            self._percept = ('clear',None)
        
        return do
        
    def mapAction(self, action):
        """Map vacuum action to pacman action"""
        if action == "GoRight": self._dir += 1
        elif action == "GoLeft": self._dir -= 1
        elif action == "GoBack": self._dir += 2
        elif action == "GoForward": pass
        elif action == "Stop": return 'Stop'
        else: return "Nothing"
        self._dir %= 4
        
        return self._dirsMap[self._dirs[self._dir]]

    def update_state_with_percept(self, percept, state):
        """Update the agents state based on a percept"""
        return state

    def choose_action(self, state): 
        """Choose an action: GoLeft, GoRight, GoForward, GoBack, Stop"""
        return random.choice(self._actions)

    def update_state_with_action(self, action, state):
        """Update 'state' based on previous action"""
        return state

    def bfs(self, state):
        print("*** Start search ***")
        explored = []
        frontier = [state]
        while frontier != []:
            # Get next node
            node = frontier.pop(0)
            
            # Timeout
            if len(explored) % 100 == 0:
                print("Expanded: " + str(len(explored)))
                print("Frontier: " + str(len(frontier)))
                print()

            if len(explored) > 10000:
                print("Out of memory: No solution found")
                return ["Stop"]

            # Graph search
            duplicate = False
            for old in explored:
                if old.is_equivalent(node): duplicate = True
            if duplicate: continue

            # Goal test
            if node.contains_food() == False:
                solution = node.get_actions()
                if solution == None: solution = []
                solution += ["Stop"]
                print("Solution found:")
                print("Solution:", solution)
                print("Expanded:", len(explored))
                print("Frontier:", len(frontier))
                return solution

            # Generate successors
            r = node.move_right()
            if r != None: frontier += [r]
            f = node.move_forward()
            if f != None: frontier += [f]
            l = node.move_left()
            if l != None: frontier += [l]
            b = node.move_back()
            if b != None: frontier += [b]

            # Explored
            explored += [node]

        print("No solution found, aborting search...")
        return ["Stop"]


class ZeroIntelligent(BaseAgent):
    class State:
        def __init__(self):
            self.actions = ["GoRight", "GoLeft", "GoForward", "GoBack"]

    def choose_action(self, state):
        action = random.choice(state.actions)
        print("Performing action:", action)
        return action
    
    
class Intelligent(BaseAgent):
    class State:
        def __init__(self):
            self.bump = False
            self.previous_action = ""
            self.actions = ["GoRight", "GoLeft", "GoForward", "GoBack"]

        def __repr__(self):
            if self.bump:
                return self.previous_action + " resulted in a bump"
            else:
                return self.previous_action
    
    def update_state_with_percept(self, percept, state):
        if percept[1] == "bump":
            state.bump = True
        else:
            state.bump = False
        return state

    def choose_action(self, state):
        actions = state.actions
        if state.bump:
            actions.remove(state.previous_action)
        return random.choice(actions)

    def update_state_with_action(self, action, state):
        state.previous_action = action
        # Print the representation (i.e. __repr__) of the state
        print(state)
        return state    
    

class SmallIntelligent(BaseAgent):
    class State:
        def __init__(self):
            self.actions = ["GoRight", "GoLeft", "GoForward", "GoBack"]

    def choose_action(self, state):
        action = random.choice(state.actions)
        print("Performing action:", action)
        return action    
    
    def getAction(self, state):            
        pos_places = state.getLegalActions()
        scores = []
        states = []
        for pos in pos_places:
            new_state = state.generatePacmanSuccessor(pos)
            score = new_state.getScore()
            scores.append(score)
            states.append(new_state)
        
        indexes = []
        max_score = max(scores)
        i = 0
        for s in scores:
            if s == max_score:
                indexes.append(i)
            i += 1
        move_i = random.choice(indexes)    
        
        return pos_places[move_i]
    
class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self):
        return not self.elements
    
    def put(self, x):
        self.elements.append(x)
    
    def get(self):
        return self.elements.popleft()    
    
class BehaviourTree(BaseAgent):
    class State:
        def __init__(self):
            self.has_path = False
            self.route = None
            self.pos = None
            self.actions = ["GoRight", "GoLeft", "GoForward", "GoBack"]

    def choose_action(self, state):
        action = random.choice(state.actions)
        print(state.route)
        next_state = state.route.pop()
        next_pos = next_state.getPacmanPosition()
        next_dir = next_state.getPacmanState().getDirection()
        print(next_dir)
        if next_pos[0] > state.pos:
            pass
        return action

    def getAction(self, state):
        #foodsLeft = state.getNumFood()
        if not self._state.has_path:
            self._state.route = self.find_path(state)
            self._state.has_path = True
            self._state.pos = state.getPacmanPosition()
        do = self.mapAction(self.choose_action(self._state))
        return do
    
    def get_neighbors(self, state):
        states = []
        legal_moves = state.getLegalActions()        
        for move in legal_moves:
            new_state = state.generatePacmanSuccessor(move)
            states.append(new_state)
        return states

    def find_path(self, state):
        frontier = Queue()
        frontier.put(state)
        
        came_from: Dict[State, Optional[State]] = {}
        came_from[state] = None
        
        while not frontier.empty():
            current = frontier.get()
            for next in self.get_neighbors(current):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
                    pos = next.getPacmanPosition()
                    if state.getFood()[pos[0]][pos[1]] == True:
                        return came_from
