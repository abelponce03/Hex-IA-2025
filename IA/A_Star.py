import math
from IA.priorityQueue import PriorityQueue
from config import COLORS
from hexagon import Hexagon
from win_condition import check_win

class Problem(object):
    def __init__(self, initial=None, goal=None, **kwds): 
        self.__dict__.update(initial=initial, goal=goal, **kwds) 
        
    def actions(self, state):        raise NotImplementedError
    def result(self, state, action): raise NotImplementedError
    def is_goal(self, state):        return state == self.goal
    def action_cost(self, s, a, s1): return 1
    def h(self, node):               return 0
    
    def __str__(self):
        return '{}({!r}, {!r})'.format(
            type(self).__name__, self.initial, self.goal)
        
        
class HexagonProblem(Problem):
    def __init__(self, game):
        self.game = game
        self.player = 2  # Jugador IA
        self.size = game.board_size
        initial_state = self.get_state_representation()
        super().__init__(initial=initial_state)

    def get_state_representation(self):
        return frozenset((pos, hex.color) for pos, hex in self.game.board.items())

    def actions(self, state):
        actions = []
        current_board = dict(state)
        for pos, color in current_board.items():
            if not color:  # Hexágono vacío
                # Extraer las coordenadas q, r de la posición
                if isinstance(pos, str):
                    q, r = eval(pos)
                else:
                    q, r = pos
                
                # Verificar si el movimiento es válido
                if not self.game.first_turn_blocked or (q, r) != (-5, 5):
                    actions.append((q, r))
        return actions

    def result(self, state, action):
        new_state = dict(state)
        q, r = action
        new_state[(q, r)] = COLORS['player2']
        return frozenset(new_state.items())

    def is_goal(self, state):
        temp_game = self.game.clone()
        
        # Convertir el estado en un tablero adecuado
        board = {}
        for pos, color in state:
            # Extraer las coordenadas q, r de la posición
            if isinstance(pos, str):
                q, r = eval(pos)
            else:
                q, r = pos
                
            # Crear hexágono con las coordenadas y el color asignado
            hex = Hexagon(q, r)
            hex.color = color
            board[pos] = hex
        
        temp_game.board = board
        return check_win(2, temp_game.board)

    def h(self, node):
        # Heurística: distancia mínima al borde objetivo
        min_distance = float('inf')
        state_dict = dict(node.state)
        
        for pos, color in node.state:
            if color == COLORS['player2']:
                # Extraer las coordenadas q, r de la posición
                try:
                    if isinstance(pos, str):
                        q, r = eval(pos)
                    else:
                        q, r = pos
                    
                    if self.player == 2:
                        # Para el jugador 2, queremos llegar al borde inferior (r=0)
                        distance = abs(r)
                        min_distance = min(min_distance, distance)
                except:
                    continue
                    
        return min_distance if min_distance != float('inf') else 0
    

class Node:
    "A Node in a search tree."
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.__dict__.update(state=state, parent=parent, action=action, path_cost=path_cost)

    def __repr__(self): return '<{}>'.format(self.state)
    def __len__(self): return 0 if self.parent is None else (1 + len(self.parent))
    def __lt__(self, other): return self.path_cost < other.path_cost
    
    
failure = Node('failure', path_cost=math.inf) # Indicates an algorithm couldn't find a solution.
cutoff  = Node('cutoff',  path_cost=math.inf) # Indicates iterative deepening search was cut off.
    
    
def expand(problem, node):
    "Expand a node, generating the children nodes."
    s = node.state
    for action in problem.actions(s):
        s1 = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s1)
        yield Node(s1, node, action, cost)
        

def path_actions(node):
    "The sequence of actions to get to this node."
    if node.parent is None:
        return []  
    return path_actions(node.parent) + [node.action]


def path_states(node):
    "The sequence of states to get to this node."
    if node in (cutoff, failure, None): 
        return []
    return path_states(node.parent) + [node.state]


def best_first_search(problem, f):
    "Search nodes with minimum f(node) value first."
    node = Node(problem.initial)
    frontier = PriorityQueue([node], key=f)
    reached = {problem.initial: node}
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            s = child.state
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                frontier.add(child)
    return failure

def g(n): return n.path_cost

def astar_search(problem, h=None):
    """Search nodes with minimum f(n) = g(n) + h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=lambda n: g(n) + h(n))