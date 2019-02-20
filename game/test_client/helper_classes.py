from move import Move

def coordinate_from_direction(x, y, direction):
    """(int, int, str) -> (int, int)
    Returns the resulting (x, y) coordinates after moving in a <direction> from <x> and <y>.
    """
    if direction == 'LEFT':
        return (x-1, y)
    if direction == 'RIGHT':
        return (x+1, y)
    if direction == 'UP':
        return (x, y-1)
    if direction == 'DOWN':
        return (x, y+1)

class Map: # all outputs will be of the form (x, y). i.e., (c, r).
    def __init__(self, map_grid):
        """(___) -> None
        Initialize a new Map.
        """
        self.grid = map_grid

    def get_tile(self, x, y):
        """(int, int) -> str
        Returns the tile found at <x> and <y>.
        
        Preconditions: x >= 0
                       y >= 0
        """
        return self.grid[y][x]

    def is_wall(self, x, y):
        """(int, int) -> bool
        Returns whether the tile at <x> and <y> is a wall.
        
        Preconditions: x >= 0
                       y >= 0
        """
        return self.grid[y][x].lower() == 'x'

    def is_resource(self, x, y):
        """(int, int) -> bool
        Returns whether the tile at <x> and <y> is a resource.
        
        Preconditions: x >= 0
                       y >= 0
        """
        return self.grid[y][x].lower() == 'r'

    def find_all_resources(self):
        """(None) -> [(int, int)]
        Returns the (x, y) coordinates for all resource nodes.
        """
        locations = []
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                if self.is_resource(col, row):
                    locations.append((col, row))
        return locations

    def closest_resources(self, unit):
        """(Unit) -> (int, int)
        Returns the coordinates of the closest resource to <unit>.
        """
        locations = self.find_all_resources()
        c, r = unit.position()
        result = None
        so_far = 999999
        for (c_2, r_2) in locations:
            dc = c_2-c
            dr = r_2-r
            dist = abs(dc) + abs(dr)
            if dist < so_far:
                result = (c_2, r_2)
                so_far = dist
        return result


class Units:
    def __init__(self, units):
        """(___) -> None
        Initialize a new Units.
        """
        self.units = {} # a dictionary of unit objects.
        for unit in units:
            self.units[str(unit['id'])] = Unit(unit)

    def get_unit(self, id):
        """(str) -> Unit
        Return the Unit with <id>.
        """
        return self.units[id]

    def get_all_unit_ids(self):
        """(None) -> [str]
        Returns the id of all current units.
        """
        all_units_ids = []
        for id in self.units:
            all_units_ids.append(id)
        return all_units_ids
    
    def get_all_unit_of_type(self, type):
        """(str) -> [Unit]
        Returns a list of unit objects of a given type.
        """
        all_units = []
        for id in self.units:
            if self.units[id].type == type:
                all_units.append(self.units[id])
        return all_units

class Unit:
    def __init__(self, attr):
        """(___) -> None
        Initialize a new Unit.
        """
        self.attr = attr
        self.type = attr['type'] # 'worker' or 'melee'.
        self.x = attr['x']
        self.y = attr['y']
        self.id = attr['id']

    def position(self):
        """(None) -> int, int
        Returns the current position of this Unit.
        """
        return self.x, self.y

    def direction_to(self, pos):
        """((int, int)) -> Direction
        Returns the direction from a unit to <pos>.
        """
        if self.y < pos[1]:
            return 'DOWN'
        elif self.y > pos[1]:
            return 'UP'
        elif self.x > pos[0]:
            return 'LEFT'
        elif self.x < pos[0]:
            return 'RIGHT'

    def move(self, *directions):
        """(___) -> Move
        Returns a Move for this Unit using the given <*directions>.
        """
        return Move(self.id, *directions)
 
    def move_towards(self, dest):
        """((int, int)) -> Move
        Return a Move for this Unit towards <dest>.
        """
        direction = self.direction_to(dest)
        return Move(self.id, direction)

    def nearby_enemies_by_distance(self, enemy_units):
        """(Units) -> [(str, int)]
        Returns a sorted list of ids and their distances (in a tuple).
        """
        x = self.x
        y = self.y
        enemies = []
        
        for id in enemy_units.units:
            unit = enemy_units.get_unit(id)
            dist = abs(x - unit.x) + abs(y - unit.y)
            enemies.append((str(unit.id), dist))
            
        enemies.sort(key=lambda tup: tup[1])
        return enemies
    
    def attack(self, *directions):
        """(___) -> Move
        Return an 'attack' Move for this Unit in the given <*directions>.
        """
        return Move(self.id, 'ATTACK', *directions)

    def can_attack(self, enemy_units): # make this a new function called attack_list and make can_attack a directed function at an enemy unit.
        """(Units) -> [(Unit, Direction)]
        Returns a list of enemy Unit that can be attacked and the direction needed to attack them.(?)
        """
        enemies = []
        for id in enemy_units.units:
            unit = enemy_units.get_unit(id)
            direction = self.direction_to((unit.x, unit.y))
            if coordinate_from_direction(self.x, self.y, direction) == (unit.x, unit.y):
                enemies.append((unit, direction))
        return enemies

    def can_duplicate(self, resources):
        """(int) -> bool
        Returns if this Unit can duplicate.
        """
        if self.type == 'melee' and self.attr['resource_cost'] <= resources and self.attr['duplication_status'] <= 0:
            return True
        else:
            return False
    
    def can_mine(self, game_map):
        """(Map) -> bool
        Returns if this Unit can mine.
        """
        if self.type == 'worker' and game_map.is_resource(self.x, self.y) and self.attr['mining_status'] <= 0:
            return True
        else:
            return False

    def mine(self):
        """(None) -> Move
        Returns a 'mine' Move for this Unit.
        """
        return Move(self.id, 'MINE')

    def duplicate(self, direction):
        """(Direction) -> Move
        Returns a 'duplicate' Move for this Unit in the given <direction>.
        """
        return Move(self.id, 'DUPLICATE', direction)

    def bfs(self, game_map, dest):
        """(Map, (int, int)) -> [(int, int)]
        Finds the shortest path from current location to dest. Returns a list where the first entry is current position.
        """
        graph = game_map.grid
        start = (self.x, self.y)
        queue = [[start]]
        vis = set(start)
        if start == dest:
            return None
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            r = node[1]
            c = node[0]
            
            if node == dest:
                return path
            for adj in ((c+1, r), (c-1, r), (c, r+1), (c, r-1)):
                if (graph[adj[1]][adj[0]] == ' ' or graph[adj[1]][adj[0]] == 'R') and adj not in vis:
                    queue.append(path + [adj])
                    vis.add(adj)
