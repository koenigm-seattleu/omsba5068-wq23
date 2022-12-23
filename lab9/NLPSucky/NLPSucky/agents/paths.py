from agents.shortestpath import shortest_path

def go_home(self):
    return [('path', self.path_home())]
    
def path_home(self):
    return shortest_path(self.worldmodel.current_position, 
                         (1,1), 
                         self.worldmodel.squares_without_walls())

def path_to_exactly(self, object_type):
    best_path = None
    nowall = self.worldmodel.squares_without_walls()
    for square in self.worldmodel.squares_with_state(object_type):
        p = shortest_path(self.worldmodel.current_position, square, nowall)
        if p and (best_path == None or len(p) < len(best_path)):
            best_path = p
    return best_path

def path_to_any(self, object_type):
    nowall = self.worldmodel.squares_without_walls()
    squares = self.worldmodel.squares_with_state(object_type)
    if len(squares) > 0:
        return shortest_path(self.worldmodel.current_position, squares[0], nowall)
    else:
        return None

def path_from_to_position(self, p1, p2):
     return shortest_path(p1,p2,self.worldmodel.squares_without_walls())
    
def path_to_position(self, position):
     return shortest_path(self.worldmodel.current_position, position,self.worldmodel.squares_without_walls())