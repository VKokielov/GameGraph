# GameGraph -- implementation

## Introduction
This document describes the gamegraph.py file, the implementation of the directed graph used to help solve recreational game puzzles that can be represented by state graphs.

Read the Theory.md document for preliminaries.  The individual python modules for derived classes and specific games are described in separate files

## Overview

### Classes

The following classes are implemented in gamegraph.py:
. **GameGraph**: This class represents the entire graph.  The graph is managed as a dictionary of state vertices, each identified by a unique key.  The key must be usable as a python dictionary key.  See the Detailed section below for details.  Note that graphs can be created in both lazy and eager mode.
. **GameVertex**: This class represents a vertex in the graph and stores outgoing and incoming edges
. **GameEdge**: This represents an edge in the graph.  The edge also has a name, used as the display string, and a key, used to uniquely identify the edge (though not as important as for vertices).  Because edges represent transitions or operations, the name should be readable; the algorithms produce a sequence of edges that are then printed out in order.

### Algorithms
The functions implemented in the file correspond to the standard algorithms used for finding solutions.  The idea, as described in the theory document, is always the same: a puzzle requires us to go from a source state ("all people on starting shore", "5 liter and 7 liter pitcher is empty") to a target state ("all people on ending shore", "pitcher A contains 4 liters").  (Currently, the algorithm implementations only support one target state; but there is no fundamental reason why they should -- in principle, each algorithm could support multiple target states all representing a win ("pitcher A contains 4 liters" OR "pitcher B contains 4 liters").

The following functions are implemented.  For details, see the next section
. **bfs_solve**: [Breadth first search](https://en.wikipedia.org/wiki/Breadth-first_search).  This function takes a graph, a source and a destination -- then returns the shortest (unweighted) path from source to destination as a list of GameEdge objects.
. **dfs_search**: [Depth first search](https://en.wikipedia.org/wiki/Depth-first_search).  This function is actually a Python generator, meaning it can (and should) be used in iterations.  The function finds all possible paths from source to destination and constructs an "edge stack" every time it hits the end-point.  This is a list, which is then yielded.  (The list is not copied and should not be modified by the user of the generator).  This function can be used to generate all solutions.
. **dijkstra**: [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm).  Assumes that edge objects have a get_weight() method which returns the edge weight.  As the other two algorithms, returns a list of edges representing the steps that should be taken from the start to the end

## Details

### GameGraph
The GameGraph is intended as a base class.  It receives two Python classes, state_class assumed to be a subclass of GameVertex, and trans_class assumed to be a subclass of GameEdge.  It also takes a "mode" argument.  The difference between different modes is described below.

. In **eager** mode, the entire game graph is generated at once.  This is done by calling, first, the "define_states" function to generate the vertices; then, for each vertex, the "add_transitions" function is called to generate the outgoing transitions for each vertex in order.
. In **lazy** mode the define_states function is not called at all.  Instead, the graph exists only "latently", as a sort of stream.  Pieces of the graph are then generated when BFS and DFS are invoked, inside the iter_from() function on GameVertex, which normally iterates through already existing edges going from a vertex to others.  (Currently Dijkstra's algorithm supports only eager graphs.)  The benefit of lazy mode is that only vertices connected to the source are generated -- which is all that is needed for solving puzzles.  This forestalls any need for cleverly constructing the graph.

(NB: It is possible to implement a third, "compromise" mode which takes one source vertex and then, in a cascading way, generates reachable target states -- but this is effectively what BFS does anyway, so for BFS it is a waste of time.  For DFS it may also be a waste of space if the object is not to find ALL solutions but just one.  For Dijkstra it may make sense.)

The graph itself is a Python dictionary of GameVertex objects.  The **keys** in this dictionary are objects -- strings or otherwise -- that uniquely identify each state.  They must support the [Python hashable protocol](https://docs.python.org/3/glossary.html#term-hashable) (i.e. they implement the special 'hash' and 'eq' methods).  The keys are very important because they are the sole way of identifying state vertices to this base class.

Specifically, both define_states and add_transitions are designed to be general for both lazy and eager mode -- as well as the other methods.  To achieve this, the derived class from GameGraph, which represents a specific graph, and the derived class from GameVertex implement the following methods:
. **gen_all_keys**: is a generator (or returns an iterator) for keys for each state in the graph
. **gen_outgoing_keys**: is a generator (or returns an iterator) for generating the keys of vertices reachable from the given vertex.  This is usually straightforward in a state graph.

Below are descriptions of the methods of this object.
. **define_states**: In eager mode, go through all possible keys and call create_state() on each, resulting in its creation and addition to the graph.
. **add_transitions**: For a given source state (GameVertex) OBJECT, if in eager mode, finds each outgoing state (since it must have been created by define_states above); if in lazy mode, create each state.  Next, create an instance of the right GameEdge.  Call the is_valid() function on this instance -- some edges may not be valid.  Finally, call link() to add the edge to the vertices.  At the end of this process, calls set_has_edges() to set a flag on the GameVertex specifying that edges have been created (and that therefore this function doesn't need to be called for this state again).
. **find_state**: Looks up an existing state in the graph
. **create_state**: If a state exists, acts the same way as find_state().  Otherwise creates a GameVertex() object of the right class, and checks whether it is valid.  As with edges, some vertices may be invalid.  For example, in the WGC problem, the state "wolf and goat on origin shore, cabbage and boat on target shore" is invalid, because it leaves the wolf and goat alone on a shore, a situation precluded by the problem's condition.  add_state() is called to add the state to the grah
. **add_state**: Adds a state to the graph.
. **link**:  Given an edge object, adds it to both the source and destination vertices.  This is needed for the iter_from and iter_to functions on each GameVertex, although all three algorithms thus far use only iter_from().

### GameVertex
The GameVertex is a base class for a single state in the game, such as "wolf, cabbage, goat, boat all on origin shore" or "wolf and cabbage on origin, goat and boat on destination."

Besides storing a reference to the graph that contains it, the GameVertex also stores a key.  The is_valid() function is implemented by subclasses to indicate that a state is valid.  add_edge() is used for bookkeeping -- it adds a reference to a GameEdge() object into the dictionary.  Note that edges also have keys, but these keys are far less important; they must, however, still be distinct for different edges.

The iter_to() and iter_from() functions return iterators of edges (note: edges!) or transitions to resp. from the object.

The __iter__() function which I have not used but which can be used to "iterate" a vertex, chains the edges from and to a vertex.

### GameEdge
The GameEdge class is also a base class.  It is far simpler than the other two classes.  It stores two keys to states (the source and destination), which makes it enough to identify the edge uniquely.  The functions are so self-explanatory that they don't require any explanation, except to note that the "name" is used to represent the edge as a string and is important for displaying solutions.  After all, an "edge" or "transition" is a step.