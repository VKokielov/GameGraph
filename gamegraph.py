import itertools
import queue

class GameEdge(object):
    def __init__(self,src,dest,graph):
        self.src_key = src.get_key()
        self.dest_key = dest.get_key()
        self.graph = graph

    def set_key(self,key):
        self.key = key

    def set_name(self,name):
        self.name = name

    def get_key(self):
        return self.key

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_src_key(self):
        return self.src_key

    def get_dst_key(self):
        return self.dest_key

    def is_valid(self):
        return True

class GameVertex(object):
    def __init__(self,key,graph):
        self.edges_in = dict()
        self.edges_out = dict()
        self.key = key
        self.has_edges = False
        self.graph = graph

    def set_has_edges(self):
        self.has_edges = True
        
    def __str__(self):
        return str(self.key)

    def get_key(self):
        return self.key

    def is_valid(self):
        return True

    def add_edge(self,edge):
        my_key = self.get_key()

        if my_key == edge.get_src_key():
            is_from_me = True
        elif my_key == edge.get_dst_key():
            is_from_me = False
        else:
            raise RuntimeError("Cannot add unrelated edge")

        target_dict = self.edges_out if is_from_me else self.edges_in

        edge_key = edge.get_key()
        if edge_key in target_dict:
            raise RuntimeError("Edge {} has the same key as another edge in vertex {}".format(str(edge), str(self)))

        target_dict[edge_key] = edge

    def iter_to(self):
        if not self.has_edges:
            raise RuntimeError("Iterating before edges are created -- call iter_from() first")
        return map(lambda p: p[1],self.edges_in.items())

    def iter_from(self):
        if not self.has_edges:
            # Need to create edges before i can iterate
            self.graph.add_transitions(self)
        return map(lambda p: p[1],self.edges_out.items())

    def __iter__(self):
        return itertools.chain(self.iter_from(),self.iter_to())
                                                            

class GameGraph(object):

    def __init__(self,state_class,trans_class,mode):
        self.graph = dict()
        self.state_class = state_class
        self.trans_class = trans_class
        self.mode = mode

        if mode == "eager":
            # Create the vertices
            self.define_states()
            # Create the edges
            for key,vx in self.graph.items():
                self.add_transitions(vx)
        elif mode != "lazy":
            raise RuntimeException("GameGraph mode must be 'eager' or 'lazy'")

    def define_states(self):
        # Generate all the keys
        # NOTE:  The derived class has the right to throw an exception in gen_all_keys(), indicating that it refuses
        # to function in eager mode
        for state_key in self.gen_all_keys():
            state = self.create_state(state_key)
        
    def add_transitions(self,source_state):
            
        # This function is used for the eager case.  All target vertices must exist
        # iterate through the outgoing keys of the vertex.  Create transitions to correspond to each key
        src_key = source_state.get_key()
        for dest_key in source_state.gen_outgoing_keys():
            if self.mode == "eager":
                dest_state = self.find_state(dest_key)
            else: # Lazy.  Create the state now
                dest_state = self.create_state(dest_key)

            if dest_state is None:  # This is not an error -- invalid states are not created. Continue to the next key
                continue

            edge = self.trans_class(source_state,dest_state,self)
            if not edge.is_valid():
                continue
            
            self.link(edge)

        # Let the vertex know that its outgoing edges exist
        source_state.set_has_edges()

    def find_state(self,key):
        return self.graph.get(key)

    def create_state(self,key):
        # Create a state
        if key in self.graph:
            return self.graph[key]

        #print ("key {}; graph size before add {}".format(str(key),str(len(self.graph))))
        
        vertex_obj = self.state_class(key,self)
        if not vertex_obj.is_valid():
            return None

        # Add the state to the dictionary
        self.add_state(vertex_obj)

        return vertex_obj
        
    def add_state(self,vertex):
        vx_key = vertex.get_key()

        if vx_key in self.graph:
            raise RuntimeError("state with key {} already in graph".format(str(vx_key)))

        self.graph[vx_key] = vertex

        #print ("cur states {}".format(self.graph))

    def link(self,edge):
        source_key = edge.get_src_key()
        dest_key = edge.get_dst_key()

        if source_key not in self.graph:
            raise RuntimeError("Edge source {} not in graph".format(source_key))

        if dest_key not in self.graph:
            raise RuntimeError("Edge destination {} not in graph".format(dest_key))

        source_vertex = self.graph[source_key]
        dest_vertex = self.graph[dest_key]

        source_vertex.add_edge(edge)
        dest_vertex.add_edge(edge)

    def iterate_states(self):
        return self.graph.items()

# bfs_solve always finds the shortest path through an unweighted state graph for a puzzle
def bfs_solve(graph,src,dst):
    # Construct a BFS tree for all vertices and use it to give the shortest path to the solution state
    bfs_tree = {src : None}

    bfs_queue = queue.Queue()

    # "create_state" because in lazy mode the source may not exist yet
    src_vertex = graph.create_state(src)
    if not src_vertex:
        raise RuntimeError("source state key invalid")

    bfs_queue.put(src_vertex)

    found_state = False
    while bfs_queue.qsize() > 0:
        # Get the next queue element
        cur_vertex = bfs_queue.get()
        cur_key = cur_vertex.get_key()

        if cur_key == dst:
            # Found dst, break
            found_state = True
            break

        # Add all unvisited neighbors to the bfs queue
        for edge in cur_vertex.iter_from():
            neighbor_key = edge.get_dst_key()
            if neighbor_key not in bfs_tree:
                bfs_tree[neighbor_key] = edge
                bfs_queue.put(graph.find_state(neighbor_key))

    shortest_path = list()
    if found_state:
        # construct a shortest_path using edges
        cur_path_key = dst
        while cur_path_key != src:
            cur_edge = bfs_tree[cur_path_key]
            shortest_path.append(cur_edge)
            cur_path_key = cur_edge.get_src_key()
          #  print("new cpk {}".format(cur_path_key))
        return list(reversed(shortest_path))

    return shortest_path

class DfsState(object):
    def __init__(self,vertex,edge,graph):
        #print("visiting {}".format(vertex.get_key()))
        self.graph = graph
        self.vertex = vertex
        # "edge" is the incoming edge we followed to get to this vertex
        # it will be None for the root of the search
        self.edge = edge
        self.children = vertex.iter_from()

    def get_vertex(self):
        return self.vertex

    def get_edge(self):
        return self.edge
    
    def get_next(self,visited):
        found_valid = False

        next_child_edge = None
        next_child = None

        while not found_valid:
            next_child_edge = next(self.children,None)
            if next_child_edge is not None:
                next_child = self.graph.find_state(next_child_edge.get_dst_key())
                found_valid = next_child.get_key() not in visited
            else:
                found_valid = True
            
        if next_child_edge is not None:
            return DfsState(next_child,next_child_edge,self.graph)

        return None

# dfs_solve is a Python generator to find all valid paths from source to dest
def dfs_solve(graph,src,dst,cycle=False):

    # If "cycle" is true, the origin is never added to the visited set
    
    dfs_stack = list()
    edge_stack = list()
    visited = set()

    if not cycle:
        visited.add(src) # for consistency

    src_vertex = graph.create_state(src)
    if src_vertex is None:
        raise RuntimeError("source state key invalid")

    dfs_stack.append(DfsState(src_vertex,None,graph))

    while dfs_stack:
        cur_state = dfs_stack[-1]
        cur_key = cur_state.get_vertex().get_key()
        #print("at {}".format(cur_key))

        if len(dfs_stack) > 1 and (cur_key == dst):
            yield edge_stack # found a solution
            
        next_state = cur_state.get_next(visited)
        if next_state is not None and ((len(dfs_stack) == 1) or (cur_key != src)):
            # Go deeper
            next_key = next_state.get_vertex().get_key()

            if src != next_key:
                visited.add(next_key)
            edge_stack.append(next_state.get_edge())
            dfs_stack.append(next_state)
        else:
            # Pop
            visited.remove(cur_state.get_vertex().get_key())
            if len(dfs_stack) > 1:
                # The dfs stack is one longer than the edge stack (because N vertices are connected by N-1 edges)
                edge_stack.pop()
            dfs_stack.pop()

# Returns whether left is less than or equal to right
# This function covers the "inf" vs "inf" case, as it should to update the initial value
def dijkstra_less(left,right):
    if left == "inf":
        return right == "inf"
    elif right == "inf":
        return True
    else:
        return left < right
 
def dijkstra(graph,src,dst):
    # Use dijkstra's algorithm to find the shortest weighted path
    dijk_dict = dict()
    dijk_parent = dict() # Keep track of the edges
    unvisited = set()
    for key,value in graph.iterate_states():
        dijk_dict[key] = "inf"
        unvisited.add(key)

   # print ("source is {}, states {}".format(str(src),str(graph)))
    if graph.find_state(src) is None:
        raise RuntimeError("source state key invalid")
        
    dijk_dict[src] = 0

    while len(unvisited) > 0:
        # Find the current vertex
        min_dist = "inf"
        min_key = None # will be update on the first compare -- see dijkstra_compare
        for key in unvisited:
            dist = dijk_dict[key]
         #   print ("key {} dist {}".format(key,dist))
            if dijkstra_less(dist,min_dist):
                min_dist = dist
                min_key = key

      #  print("min dist {}".format(min_dist))
        if min_dist == "inf":
            break
        cur_vertex = graph.find_state(min_key)
        #print ("cur vertex is {}".format(str(cur_vertex)))
        
        for neighbor_edge in cur_vertex.iter_from():
            dst_node_key = neighbor_edge.get_dst_key()
            #print("considering neighbor {}".format(str(neighbor_edge)))
            if dst_node_key in unvisited:
                cur_dist = dijk_dict[dst_node_key]
                new_dist = min_dist + neighbor_edge.get_weight()
                if dijkstra_less(new_dist,cur_dist):
                    #print("updating total path to {}".format(new_dist))
                    dijk_dict[dst_node_key] = new_dist
                    dijk_parent[dst_node_key] = neighbor_edge
                    
        unvisited.remove(min_key)

    shortest_path = list()
    if dst in dijk_parent:
        cur_path_key = dst
        while cur_path_key != src:
            cur_edge = dijk_parent[cur_path_key]
            shortest_path.append(cur_edge)
            cur_path_key = cur_edge.get_src_key()
          #  print("new cpk {}".format(cur_path_key))
        return list(reversed(shortest_path))

    return shortest_path
            
        
