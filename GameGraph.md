# GameGraph -- implementation

## Introduction
This document describes the gamegraph.py file, the implementation of the directed graph used to help solve recreational game puzzles that can be represented by state graphs.

Read the Theory.md document for preliminaries.  The individual python modules for derived classes and specific games are described in separate files

## Overview

The following classes are implemented in gamegraph.py:
. *GameGraph*: This class represents the entire graph.  The graph is managed as a dictionary of state vertices, each identified by a unique key.  The key must be usable as a python dictionary key.  See the description below for details.  Note that graphs can be created in both lazy and eager mode.
. *GameVertex*: This class represents a vertex in the graph and stores outgoing and incoming edges
. *GameEdge*: This represents an edge in the graph.  The edge also has a name, used as the display string, and a key, used to uniquely identify the edge (though not as important as for vertices).  Because edges represent transitions or operations, the name should be readable; the algorithms produce a sequence of edges that are then printed out in order.

The following functions are implemented in gamegraph.py:
* *bfs_solve* runs a breadth first search on a graph to find the shortest path between a source and destination graph.  The algorithm will work for both 
. *dfs_solve* (plus helper class *DfsState*): 