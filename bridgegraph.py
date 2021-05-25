import gamegraph

# The bridge game is always the same, with variations
# A set of objects must be transported from an origin to a destination
# via a means such as a boat, bridge, etc.
# Certain constraints exist on who can cross and when
# As a convention, we use a sorted list of object names as key components
# The key represents the set of objects on the destination shore

def get_bridge_key(graph,target_set):
    sorted_names = graph.get_sorted_objects()
    my_key = ""
    for game_obj in sorted_names:
        if game_obj in target_set:
            my_key += game_obj
            my_key += "/"

    return my_key

# Helpers for generating outgoing states
# Given a configuration of people on both shores, the function gen_outgoing_keys will generate keys representing valid states
# to transfer into
TRIP_MADE="trip_made"
TRIP_NOT_MADE="trip_not_made"
TRIP_IMPOSSIBLE="trip_impossible"

class TripCounter(object):
    def __init__(self,size):
        self.trips_made = 0
        self.trips_not_made = size
        self.trips_impossible = 0
        self.trip_list = [TRIP_NOT_MADE] * size

    def set_trip(self,idx,val):
        tlist = self.trip_list
        if tlist[idx] == TRIP_MADE:
            self.trips_made -= 1
        elif tlist[idx] == TRIP_NOT_MADE:
            self.trips_not_made -= 1
        elif tlist[idx] == TRIP_IMPOSSIBLE:
            self.trips_impossible -= 1

        tlist[idx] = val
        if tlist[idx] == TRIP_MADE:
            self.trips_made += 1
        elif tlist[idx] == TRIP_NOT_MADE:
            self.trips_not_made += 1
        elif tlist[idx] == TRIP_IMPOSSIBLE:
            self.trips_impossible += 1

class BridgeGameKey(object):
    def __init__(self,graph,target_set):
        self.target_set = set(target_set)
        self.cached_string_key = get_bridge_key(graph,self.target_set)

    def __hash__(self):
        return hash(self.cached_string_key)

    def __eq__(self,other):
        return self.cached_string_key == str(other)

    def __str__(self):
        return self.cached_string_key

    def get_target_set(self):
        return self.target_set  

class BridgeGameVertex(gamegraph.GameVertex):
    # Generate transitions between states for the case of a boat, a flashlight, etc that supports N objects
    # The boat or flashlight is itself an object, but obviously its behavior is fixed by its position in the source state
    # The other objects move with the boat
    # This function works by enumerating all transitions and selecting those which move the right number of objects in the right direction
    # A faster function would select subsets directly, but is harder to understand and implement

    def gen_outgoing_keys(self):
        arities = self.graph.arities
        carrier = self.graph.carrier

#        print("source vx {}".format(src_vx.get_key()))
        src_set = self.key.get_target_set()
        state_card = len(self.graph.sorted_objects)
        # Precompute: create the flag list, the template, the initial xor...
        flag_list = [False] * (state_card+1)
        template_list = [False] * state_card
        trip_counter = TripCounter(state_card)
        carrier_idx = -1
        carrier_on_dest = carrier in src_set
        objnames = self.graph.sorted_objects

#        print("\n\n\nsource vertex {}".format(src_vx))       
        for idx in range(0,state_card):
#            print ("init considering object {}".format(self.sorted_objects[idx]))
            if objnames[idx] == carrier:
                carrier_idx = idx
                flag_list[idx] = not carrier_on_dest
            else:
                template_list[idx] = objnames[idx] in src_set

                trip = TRIP_NOT_MADE if not template_list[idx] else (TRIP_MADE if carrier_on_dest == template_list[idx] else TRIP_IMPOSSIBLE)
#                print("trip {}".format(trip))
                trip_counter.set_trip(idx, trip)

        current_set = set()
        if not carrier_on_dest:
            current_set.add(carrier)

        while not flag_list[-1]:
#            print (">>>trips made {} trips not made {} trips impossible {} for set {}".format(trip_counter.trips_made,trip_counter.trips_not_made,trip_counter.trips_impossible,get_bridge_key(self,current_set)))
            if trip_counter.trips_impossible == 0 and trip_counter.trips_made in arities:
                outgoing_key = BridgeGameKey(self.graph,current_set)
                yield outgoing_key

            # Update
            for idx in range(0,state_card+1):
                # NOTE:  The carrier's motion is fixed
 #               if idx < state_card:
 #                   print ("considering object {}".format(self.sorted_objects[idx]))
                if idx != carrier_idx:
                    if flag_list[idx]:
                        # Remove
                        flag_list[idx] = False
                        if idx < state_card:
                            current_set.remove(objnames[idx])
                            trip = TRIP_NOT_MADE if not template_list[idx] else (TRIP_MADE if carrier_on_dest == template_list[idx] else TRIP_IMPOSSIBLE)
#                            print("trip {}".format(trip))
                            trip_counter.set_trip(idx, trip)
                    else:
                        # Add
                        flag_list[idx] = True
                        if idx < state_card:
                            current_set.add(objnames[idx])
                            trip = TRIP_NOT_MADE if template_list[idx] else (TRIP_MADE if carrier_on_dest == template_list[idx] else TRIP_IMPOSSIBLE)
#                            print("trip {}".format(trip))
                            trip_counter.set_trip(idx, trip)
                        break        

class BridgeGameEdge(gamegraph.GameEdge):
    def __init__(self,src,dst,graph):
        # The name is determined by the set differences between the target sets
        src_target = src.get_key().get_target_set()
        dst_target = dst.get_key().get_target_set()

#        print("src {} dst {}".format(str(src_target),str(dst_target)))

        moved_to_shore = dst_target.difference(src_target)
        moved_from_shore = src_target.difference(dst_target)

        self.moved_to_shore = moved_to_shore
        self.moved_from_shore = moved_from_shore

        my_name = ""
        my_key_list = list()
        if moved_to_shore:
            my_name += "moved to destination: "
            for obj_name in moved_to_shore:
                my_key_list.append("+{}".format(obj_name))
                my_name += obj_name
                my_name += ", "
        if moved_from_shore:
            my_name += "moved to origin: "
            for obj_name in moved_from_shore:
                my_key_list.append("-{}".format(obj_name))
                my_name += obj_name
                my_name += ", "

        my_key = "/".join(sorted(my_key_list))
#        print("Created transition {} called {}".format(my_key,my_name))
        super().__init__(src,dst,graph)
        super().set_key(my_key)
        super().set_name(my_name)
        

class BridgeGameGraph(gamegraph.GameGraph):
    def __init__(self,objects,mode,state_class=BridgeGameVertex,trans_class=BridgeGameEdge):
        if len(set(objects)) < len(objects):
            raise RuntimeError("Objects have duplicate names")
       
        objects = sorted(objects)
        self.sorted_objects = objects

        super().__init__(state_class,trans_class,mode)

    def get_sorted_objects(self):
        return self.sorted_objects

    def gen_all_keys(self):
        # A tricky procedure, but commonplace
        # Construct all subsets.  Warning: EXPONENTIAL!
        # Each target set is checked using the derived class's verify_state() function

        state_card = len(self.sorted_objects)
        flag_list = [False] * (state_card+1)
        current_set = set()

        while not flag_list[-1]:
            new_key = BridgeGameKey(self,current_set)
            yield new_key # Someone is asking for the key
                
            # Remove all elements on the other shore and add the first one that isn't
            for idx in range(0,state_card+1):
                if flag_list[idx]:
                    # Remove
                    if idx < state_card:
                        current_set.remove(self.sorted_objects[idx])
                    flag_list[idx] = False
                else:
                    # Add
                    if idx < state_card:
                        current_set.add(self.sorted_objects[idx])
                    flag_list[idx] = True
                    break

class GoatBridgeGameVertex(BridgeGameVertex):
    # This function defines whether the vertex represents a valid state for the goat/wolf/cabbage game
    def is_valid(self):
        state_set = self.key.get_target_set()
        if "boat" not in state_set:
            goat_on_shore = "goat" in state_set
            wolf_on_shore = "wolf" in state_set
            cabbage_on_shore = "cabbage" in state_set
        else:
            goat_on_shore = "goat" not in state_set
            wolf_on_shore = "wolf" not in state_set
            cabbage_on_shore = "cabbage" not in state_set

        return not (goat_on_shore and wolf_on_shore) and not (goat_on_shore and cabbage_on_shore)        

class GoatBridgeGameGraph(BridgeGameGraph):
    BRIDGE_OBJ_LIST = ["goat","wolf","cabbage","boat"]
    def __init__(self,mode):
        # The boat in the goat problem can only carry up to one passenger (the man is for the purposes of this puzzle a permanent fixture of the boat)
        # Up to: the boat can go empty too and indeed must
        self.arities = set([0,1])
        # For generating the vertices, we need to know which object is the carrier
        self.carrier = "boat"

        super().__init__(GoatBridgeGameGraph.BRIDGE_OBJ_LIST,mode,state_class=GoatBridgeGameVertex)

class CrossingAtNightEdge(BridgeGameEdge):
    def __init__(self,src,dst,graph):
        super().__init__(src,dst,graph)
        # The weight is assigned with the help of the graph
        # According to the problem specification, the weight is the maximum of all the weights of the objects
        # that crossed the river (obviously, in the same direction)

        if len(self.moved_from_shore) > 0:
            moved_set = self.moved_from_shore
        elif len(self.moved_to_shore) > 0:
            moved_set = self.moved_to_shore

        max_weight = 0
        for obj in moved_set:
            cur_weight = graph.transit_weight(obj)
            if cur_weight > max_weight:
                max_weight = cur_weight

        self.weight = max_weight

        self.set_name("{} (weight {})".format(self.get_name(),max_weight))

        #print("Constructing edge {} with weight {}".format(self.key,self.weight))

    def get_weight(self):
        return self.weight

class CrossingAtNightGraph(BridgeGameGraph):
    CROSSING_OBJ_LIST = ["flashlight", "oner", "twoer", "fiver", "tener"]
    def __init__(self):
        # NOTE: The flashlight cannot return alone, someone must bring it back
        self.arities = set([1,2])
        self.carrier = "flashlight"
        self.transit_weights = {"flashlight" : 0,
                        "oner" : 1,
                        "twoer" : 2,
                        "fiver" : 5,
                        "tener" : 10}
        
        super().__init__(CrossingAtNightGraph.CROSSING_OBJ_LIST,"eager",trans_class=CrossingAtNightEdge)

    def transit_weight(self,obj):
        return self.transit_weights[obj]


if __name__=="__main__":
    ggraph = GoatBridgeGameGraph("lazy")
    origin_key = BridgeGameKey(ggraph,set());
    destination_key = BridgeGameKey(ggraph,set(GoatBridgeGameGraph.BRIDGE_OBJ_LIST))
    shortest_path = gamegraph.bfs_solve(ggraph, origin_key, destination_key)
    print("shortest path:")
    for edge_num, path_edge in enumerate(shortest_path):
        print("{}. {}".format(edge_num+1,str(path_edge)))

    # Find all solutions
    gen_all_solv = gamegraph.dfs_solve(ggraph, origin_key, destination_key)

    print("all solutions:")
    for solution in gen_all_solv:
        for edge_num, path_edge in enumerate(solution):
            print("{}. {}".format(edge_num+1,str(path_edge)))
        print("\n\n")

    # Use dijkstra to solve the crossing at night problem
    night_graph = CrossingAtNightGraph()
    origin_key = BridgeGameKey(night_graph,set())
    destination_key = BridgeGameKey(night_graph,CrossingAtNightGraph.CROSSING_OBJ_LIST)

    print ("at night origin {}".format(origin_key)) 

    shortest_path = gamegraph.dijkstra(night_graph,origin_key,destination_key)
    print("shortest path (night crossing):")
    for edge_num, path_edge in enumerate(shortest_path):
        print("{}. {}".format(edge_num+1,str(path_edge)))



