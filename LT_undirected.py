#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

import networkx as nx

__all__ = ['linear_threshold']


def linear_threshold(graph, seeds, steps=0):
    if type(graph) == nx.MultiGraph or type(graph) == nx.MultiDiGraph:
        raise Exception("linear_threshold() is not defined for graphs with multi-edges.")

    # change to undirected graph
    if graph.is_directed():
        undirected_graph = graph.to_undirected()
    else:
        undirected_graph = copy.deepcopy(graph)


