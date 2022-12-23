from agents.searchClientInterface import WorldState
from agents.searchClientInterface import Problem
from agents.searchClientInterface import BFSEvaluator
from agents.searchFramework import aStarSearch
import copy

def shortest_path(source_pos, dest_pos, free_pos_list):
    if source_pos == dest_pos:
        return []
    path = aStarSearch(ShortestPathProblem(source_pos, dest_pos, free_pos_list), BFSEvaluator())[0]
    return path
    
class ShortestPathWorldState(WorldState):
    def __init__(self, start_position, free_squares):
        self._free_squares = free_squares
        self._position = start_position
    
    def adjacencies(self, position):
        return [p for p in self._free_squares if self.adjacent(p)]
    
    def adjacent(self, p):
        return self._position[0] == p[0] and self._position[1] == p[1] + 1 or \
                self._position[0] == p[0] and self._position[1] == p[1] - 1 or \
                self._position[1] == p[1] and self._position[0] == p[0] + 1 or \
                self._position[1] == p[1] and self._position[0] == p[0] - 1
    
    # Convenience function to make these objects print nicely
    def __str__(self):
        return "{" + str(self._position) + "}"
    
    #  These two methods are REQUIRED to make cycle checking work
    #  Notice they depend on the object's internal state, so they must
    #  be customized to each new kind of WorldState
    
    def __eq__(self, other):
        if isinstance(other, ShortestPathWorldState):
            return self._position == other._position
        else:
            return False

    def __hash__(self):
        return hash(str(self._position))
    
    # NB: every successor state must deep copy the old state!
    
    def successors(self):
        return [self.make_adjacent_state(adj) for adj in self.adjacencies(self._position)] 
    
    def make_adjacent_state(self, adjacency):
        s = copy.deepcopy(self)
        s._position = adjacency
        return (s, adjacency)
    
class ShortestPathProblem(Problem):
    def __init__(self, source_position, dest_position, free_positions):
        self._source_position = source_position
        self._dest_position = dest_position
        self._free_positions = free_positions

    def initial(self):
        return ShortestPathWorldState(self._source_position, self._free_positions)
    
    def isGoal(self, state):
        return state._position == self._dest_position
