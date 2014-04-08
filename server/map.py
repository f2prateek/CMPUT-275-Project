"""
Map module for working with map data.

It reads in map data from a file.
Each line in the file contains either a vertex or an edge
in the following format.

V(ertex),{id},{latitude},{longitude}
e.g. V,30198538,53.618369,-113.602987

E(dge),{vertex},{vertex},{name}
e.g. E,314080060,314080061,23 Avenue NW
"""

from graph import Graph

def straight_line_dist(lat1, lon1, lat2, lon2):
    """
    Computes the straightline distance between
    two points (lat1, lon1) and (lat2, lon2)
    """
    return ((lat2-lat1)**2 + (lon2-lon1)**2)**0.5


def join_path(dest, source):
    """
    Copy a source path into a destination path.
    This is different from simply extending, since if dest isn't empty
    it's last location is same as the source's start location.
    This method takes care of this case.
    """
    if len(dest) == 0:
        dest = source
    else:
        # disregard the first vertex, it will be the same as the last vertex from earlier.
        dest.extend(source[1:])

    return dest

class Map:
    def __init__(self, filename):
        """
        Construct a new map. Delegates to load_map.
        """
        self.load_map(filename)

    def load_map(self, filename):
        """
        Read in the Road Map Data from the
        given filename and create our Graph, a dictionary
        for looking up the latitude and longitude information
        for vertices and a dictionary for mapping streetnames
        to their associated edges.

        Each line in the file contains either a vertex or an edge
        in the following format.

        V(ertex),{id},{latitude},{longitude}
        e.g. V,30198538,53.618369,-113.602987

        E(dge),{vertex},{vertex},{name}
        e.g. E,314080060,314080061,23 Avenue NW
        """
        self._graph = Graph()
        self._location = {}
        self._streetnames = {}

        with open(filename, 'r') as f:
            for line in f:
                elements = line.split(",")
                if(elements[0] == "V"):
                    self._graph.add_vertex(int(elements[1]))
                    self._location[int(elements[1])] = (self.process_coord(elements[2]),
                                                  self.process_coord(elements[3]))
                elif (elements[0] == "E"):
                    self._graph.add_edge((int(elements[1]), int(elements[2])))
                    self._streetnames[(int(elements[1]), int(elements[2]))] = elements[3]

    def reconstruct_path(self, start, dest, parents):
        """
        reconstruct_path reconstructs the shortest path from vertex
        start to vertex dest.

        "parents" is a dictionary which maps each vertex to their
        respective parent in the lowest cost path from start to that
        vertex.

        >>> parents = {'l': ' ', 'e': 'l', 'a': 'e', 'h':'a'}
        >>> reconstruct_path('l', 'h', parents)
        ['l', 'e', 'a', 'h']

        """
        current = dest
        path = [dest]

        while current != start:
            path.append(parents[current])
            current = parents[current]

        path.reverse()
        return path

    def process_coord(self, coord):
        """
        given a string with a standard latitude or
        longitude coordinate convert it be in
        100, 1000ths of a degree. Truncate to be an
        int.
        """
        return int(float(coord)*100000)

    def least_cost_path(self, graph, start, dest, cost):
        """
        Using Dijkstra's algorithm to solve for the least
        cost path in graph from start vertex to dest vertex.
        Input variable cost is a function with method signature
        c = cost(e) where e is an edge from graph.

        Modified to return cost of the path as well.

        >>> graph = Graph({1,2,3,4,5,6}, [(1,2), (1,3), (1,6), (2,1), (2,3), (2,4), (3,1), (3,2), \
                (3,4), (3,6), (4,2), (4,3), (4,5), (5,4), (5,6), (6,1), (6,3), (6,5)])
        >>> weights = {(1,2): 7, (1,3):9, (1,6):14, (2,1):7, (2,3):10, (2,4):15, (3,1):9, \
                (3,2):10, (3,4):11, (3,6):2, (4,2):15, (4,3):11, (4,5):6, (5,4):6, (5,6):9, (6,1):14,\
                (6,3):2, (6,5):9}
        >>> cost = lambda e: weights.get(e, float("inf"))
        >>> least_cost_path(graph, 1, 5, cost)
        [1, 3, 6, 5]
        """
        # est_min_cost[v] is our estimate of the lowest cost
        # from vertex start to vertex v
        est_min_cost = {}

        # parents[v] is the parent of v in our current
        # shorest path from start to v
        parents = {}

        # todo is the set of vertices in our graph which
        # we have seen but haven't processed yet. This is
        # the list of vertices we have left "to do"
        todo = {start}

        est_min_cost[start] = 0

        while todo:
            current = min(todo, key=lambda x: est_min_cost[x])

            if current == dest:
                return {'cost': est_min_cost[current], 'path': self.reconstruct_path(start, dest, parents)}

            todo.remove(current)

            for neighbour in graph.neighbours(current):
                #if neighbour isn't in est_min_cost, that means I haven't seen it before,
                #which means I should add it to my todo list and initialize my lowest
                #estimated cost and set it's parent
                if not neighbour in est_min_cost:
                    todo.add(neighbour)
                    est_min_cost[neighbour] = (est_min_cost[current] + cost((current, neighbour)))
                    parents[neighbour] = current
                elif est_min_cost[neighbour] > (est_min_cost[current] + cost((current, neighbour))):
                    #If my neighbour isn't new, then I should check if my previous lowest cost path
                    #is worse than a path going through vertex current. If it is, I will update
                    #my cost and record current as my new parent.
                    est_min_cost[neighbour] = (est_min_cost[current] + cost((current, neighbour)))
                    parents[neighbour] = current

        return []

    # Find closest vertices to the provided lat and lon positions
    def find_closest_vertex(self, lat, lon):
        return min(self._location, key=lambda v:straight_line_dist(lat, lon, self._location[v][0], self._location[v][1]))

    # Define our cost_distance function that takes in an edge e = (vertexid, vertexid)
    def cost_distance(self, e):
        return straight_line_dist(self._location[e[0]][0], self._location[e[0]][1],
                                                   self._location[e[1]][0], self._location[e[1]][1])

    def _find_path_with_vertex_ids(self, vertices):
        """
        Find a path from the start coordinates to the end coordinates.
        Different from find_path in that it uses the vertex ids directly rather than
        coordinates.
        This simply returns the ids of the vertices.
        Call get_path with this path to get a more useful path.
        Takes in the raw vertex ids:
        """
        path = {'cost': 0, 'path': list()}

        for i in range(len(vertices) - 1):
            node_path = self.least_cost_path(self._graph, vertices[i], vertices[i+1], self.cost_distance)
            path['cost'] = path['cost'] + node_path['cost']
            path['path'] = join_path(path['path'], node_path['path'])

        return path
            
    def find_path(self, locations):
        """
        Find a path from the start coordinates to the end coordinates.
        This simply returns the ids of the vertices.
        Call get_path with this path to get a more useful path.
        [(5365488,-11333914),(5365488,-11333914),(5365488,-11333914)]
        """
        # Map the locations to their nearest vertex ids
        # vertices = [123, 344, 13213, 213]
        vertices = [self.find_closest_vertex(location[0], location[1]) for location in locations]

        return self._find_path_with_vertex_ids(vertices)
    
    def find_optimized_path(self, locations):
        """
        Find an optimized path to travel through the given list.

        The first location in the list is the starting point. The rest will be
        travelled to minimize the cost.

        This simply returns the ids of the vertices.
        Call get_path with this path to get a more useful path.

        locations is a list of coordinates in the format
        [(5365488,-11333914),(5365488,-11333914),(5365488,-11333914)]
        """
        # Map the locations to their nearest vertex ids
        # points = [123, 344, 13213, 213]
        vertices = [self.find_closest_vertex(location[0], location[1]) for location in locations]

        current = vertices.pop(0)
        greedy_path = [current]

        while vertices:
            nearest_vert = None
            nearest_path = {'path':list(), 'cost':float("inf")}

            #find the vertex nearest to current
            for vertex in vertices:
                route = list()
                route.append(current)
                route.append(vertex)
                #look up the path from current to this vertex
                path = self._find_path_with_vertex_ids(route)
                # check if this path is better than our old estimate
                if path['cost'] < nearest_path['cost']:
                    nearest_path = path
                    nearest_vert = vertex

            #remove it and add the path to the greedy_path
            current = nearest_vert
            vertices.remove(current)
            join_path(greedy_path, nearest_path['path'])

        return {'path':greedy_path, 'length':len(greedy_path)}

    def get_path(self, path):
        """
        Returns a dictionary of a set of data,
        length - length of the path
        points - an array of coordinates, each being a step in the path
        The coordinates are converted back to decimal form (53.45 not 534500)
        """
        points = list()
        # convert the coordinates in a way that the clients can understand
        def process(val):
          return float(val)/100000
        for v in path:
          points.append((process(self._location[v][0]), process(self._location[v][1])))

        return {'length': len(points), 'path': points}
    
    def minify_path(self, path):
        """
        Minify a path such that points on the same line are removed.
        """
        def get_direction(start, end):
            """
            Get the cardinal direction to travel in between two coordinates.

            This generalizes the map into a cartesian plane as we
            did for distance.
            """
            # get the deltas
            dy = self._location[end][1] - self._location[start][1]
            dx = self._location[end][0] - self._location[start][0]

            # use the pair with the greater delta for direction
            if abs(dy) > abs(dx):
                # use longitude
                if dy < 0 :
                    return 'south'
                else:
                    return 'north'
            else:
                # use latitude
                if dx < 0:
                    return 'west'
                else:
                    return 'east'

        def calculate_turn(start, mid, end):
            """
            Returns a tuple containing the turn to make and direction to
            follow if you're traveling in a currection of start to mid,
            and want to head to end.
            start and mid give us the direction we're currently in, to help us
            calculate the turn to make to reach end.
            mid and end give us the direction to go in.

            TODO:
            * use constants for cardinal directions here and in get_direction
            * we may, already have current_direction from the last calculation,
            reuse these for speed
            """
            current_direction = get_direction(start, mid)
            new_direction = get_direction(mid, end)

            if current_direction == 'west':
                if new_direction == 'north':
                    turn = 'right'
                else:
                    turn = 'left'
            elif current_direction == 'east':
                if new_direction == 'north':
                    turn = 'left'
                else:
                    turn = 'right'
            elif current_direction == 'north':
                if new_direction == 'east':
                    turn = 'right'
                else:
                    turn = 'left'
            else:
                if new_direction == 'east':
                    turn = 'left'
                else:
                    turn = 'right'

            return (turn, new_direction)
        
        min_path = list()
        min_path.append(path[0])
        
        current_direction = get_direction(path[0], path[1])
        
        # iterate over all except first and last
        for i in range(1, len(path) - 2):
            new_direction = get_direction(path[i], path[i+1])
            if current_direction != new_direction:
                min_path.append(path[i])
            current_direction = new_direction
            
        min_path.append(path[len(path)-1])
            
        return min_path
