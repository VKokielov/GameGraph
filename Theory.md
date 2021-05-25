# GameGraph

GameGraph is a Python-based tool for representing and solving state graphs for puzzles

## What is a state graph?
Many puzzles in recreational mathematics involve finite processes, so they can be represented naturally by a state graph.  A state graph is a mathematical directed (usually not acyclic) graph (vertices and edges) where the vertices represent the possible states of some system and the edges represent operations that take the system from one state to another.  For example, let's say you have a light bulb controlled simultaneously by two switches.  The "state space", the total set of states in which the system may be found, is the set {ON,OFF}x{ON,OFF}x{ON,OFF} with 8 elements, where, again for example:
(ON,ON,OFF)
means "first switch on, second switch on, light bulb off"
and 
(OFF,ON,ON)
means "first switch off, second siwtch on, light bulb on"

These would then be the vertices of the graph.  The edges are operations; we can define them however we find it convenient; in this case the most convenient for operations is "flip switch 1" and "flip switch 2".  Knowing this, and knowing that flipping any switch inverts the state of the light bulb, we can draw the graph for the entire system.

state 1:
(OFF,OFF,OFF)
flip1->(ON,OFF,ON)
flip2->(OFF,ON,ON)

state 2:
(ON,OFF,ON)
flip1->(OFF,OFF,OFF)
flip2->(ON,ON,OFF)

state 3:
(OFF,ON,ON)
flip1->(ON,ON,OFF)
flip2->(OFF,OFF,OFF)

state 4:
(ON,ON,OFF)
flip1->(OFF,ON,ON)
flip2->(ON,OFF,ON)

state 5:
(OFF,OFF,ON)
flip1->(ON,OFF,OFF)
flip2->(OFF,ON,OFF)

state 6:
(ON,OFF,OFF)
flip1->(OFF,OFF,ON)
flip2->(ON,ON,ON)

state 7:
(OFF,ON,OFF)
flip1->(ON,ON,ON)
flip2->(OFF,OFF,ON)

state 8:
(ON,ON,ON)
flip1->(OFF,ON,OFF)
flip2->(ON,OFF,OFF)

Note that states 1-4 are not connected to states 5-8.  The graph is partitioned into two connected sets of vertices, each of which can be represented as the state of the light bulb when both switches are OFF.

## Finding a path - eager and lazy
Often, a puzzle requests exactly the shortest (weighted or unweighted) path through a state graph:

"Once upon a time a farmer went to a market and purchased a wolf, a goat, and a cabbage. On his way home, the farmer came to the bank of a river and rented a boat. But crossing the river by boat, the farmer could carry only himself and a single one of his purchases: the wolf, the goat, or the cabbage.

If left unattended together, the wolf would eat the goat, or the goat would eat the cabbage.

The farmer's challenge was to carry himself and his purchases to the far bank of the river, leaving each purchase intact. How did he do it?"

Rewritten in terms of the puzzle's state graph, in formal language:

Consider a state space representable by 4 bits (0000 to 1111), where each bit represents a single object in the puzzle (wolf,cabbage,goat,boat+farmer).  IF a bit is 0, then the object is on shore A.  If a bit is 1, the object is on shore B.  Find the shortest path from the source state 0000 to the destination state 1111, given transitions of the type "0000"->"0101" (boat carries cabbage to the opposite shore).

This can be done with standard techniques -- in this case, with a graph search algorithm called "breadth first search".  Breadth first search keeps a queue, which at step I of the algorithm contains vertices that cannot be reached in less than I steps, but can be reached in I steps from the starting vertex.  We start at the initial state (0000) and BFS until we find the final state (1111).  Each edge is an operation (or instruction), so by retracing the edges we followed during the BFS to the destination, we can generate a list of steps and thus solve the puzzle.

Before we can search through the graph, however, we must construct it.  There are two ways to go about it:

1. Create all possible states by enumeration (in this case by enumerating all bit combinations from 0000 to 1111).  Afterward, go to each state and generate all the transitions or operations by using the state to find neighboring states
1. Do not create any state until it's needed.  As we run the BFS and request each state's neighbors, create both the edges and the neighbors, and add them to the graph.  This approach is much more space efficient when looking for one specific solution; it does not waste time or space on states which cannot be reached from the source -- like the "mirror" states 5-8 in the example above when starting with 1-4.

The choice between these two approaches depends on the algorithm used to find the solution.  (BFS is just one -- see "Other algorithms" below).  Some algorithms as implemented by default are global; they require the entire graph to exist; one such algorithm is the normal implementation of Dijkstra's weighted short path algorithm.

## Other algorithms
BFS is only one algorithm to find a solution to a puzzle.  It is used when the aim is to find the shortest unweighted path from a source state to a destination state, or else prove that it's impossible.  

Another standard algorithm, depth first search, can be used to find all solution candidates and pick the one that matches a criterion.  For example, suppose the goal is to find a hamiltonian path through the graph - a path that goes through each vertex only once.  A good brute-force approach is to run a depth first search on each vertex, stopping when you find a path that includes V-1 edges, where V is the number of vertices.  (Paths generated by depth-first-search by definition have no cycles)

When the operations in question are weighted, the unweighted searches become inadequate, and Dijkstra's algorithm should be used.  