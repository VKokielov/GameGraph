# Overview
This is the Game Graph project, a Python mini-library for building state graphs to model turn-by-turn games and other state-graph-based puzzles.

It supports:

1. Creation of state/transition graphs to find optimal solutions to simple algorithmic problems
1. Solving these problems using standard graph algorithms, specifically:
	1. *Breadth-first-search* finds the shortest path from a source to a destination state through an unweighted graph.  An example of a game that can be solved using BFS is the [Wolf, goat, cabbage problem](https://en.wikipedia.org/wiki/Wolf,_goat_and_cabbage_problem)
	1. *Depth-first-search* finds all paths from a source to a destination state, in any type of state graph
	1. *Dijkstra's algorithm* finds the shortest path from a source to a destination state in a weighted state graph.  An example of a game that can be solved using Dijkstra's algorithm is the [Bridge and torch problem](https://en.wikipedia.org/wiki/Bridge_and_torch_problem#A_semi-formal_approach)

# Documents
The first document in the following list is a high-level introduction to the theory of this solver.  The others are descriptions of the modules
. [Theory](Theory.md)
. [GameGraph](GameGraph.md)
. [BridgeGraph](BridgeGraph.md)