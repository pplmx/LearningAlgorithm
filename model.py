#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy

import networkx as nx

__all__ = ['linear_threshold']


# -----------------------------------
#  Diffusion Models
# -----------------------------------

def linear_threshold(graph, seeds, steps=0):
    """
    Parameters
    ----------
    graph : networkx graph
        The number of nodes.
    seeds: list of nodes
        The seed nodes of the graph
    steps: int
        The number of steps to diffuse
        When steps <= 0, the model diffuses until no more nodes
        can be activated
    Return
    ------
    layer_i_nodes : list of list of activated nodes
      layer_i_nodes[0]: the seeds
      layer_i_nodes[k]: the nodes activated at the kth diffusion step
    Notes
    -----
    1. Each node is supposed to have an attribute "threshold".  If not, the
       default value is given (0.5).
    2. Each edge is supposed to have an attribute "influence".  If not, the
       default value is given (out_deg / out_deg_sum)
    3. edge(u, v)'s influence = u's out_deg / u's all adjacency in_edges' nodes' out_deg_sum
    """
    if type(graph) == nx.MultiGraph or type(graph) == nx.MultiDiGraph:
        raise Exception("linear_threshold() is not defined for graphs with multi-edges.")

    # make sure the seeds are in the graph
    for seed in seeds:
        if seed not in graph.nodes():
            raise Exception("seed", seed, "is not in graph")

    # change to directed graph
    if not graph.is_directed():
        # directed_graph = graph.to_directed()
        directed_graph = nx.DiGraph(graph)
    else:
        directed_graph = copy.deepcopy(graph)

    # >>>>>>>>>> init thresholds <<<<<<<<<<
    """
    >>> list(graph.nodes)
    [0, 1, 2]
    >>> list(graph)
    [0, 1, 2]
    """
    for i, threshold in directed_graph.nodes(data='threshold'):
        if threshold is None:
            directed_graph.nodes[i]['threshold'] = 0.5
        elif threshold > 1:
            raise Exception("Node error: The threshold of node-{} cannot be larger than 1.".format(i))

    # >>>>>>>>>> init influences <<<<<<<<<<
    """
    >>> [e for e in graph.edges]
    [(0, 1), (1, 2), (2, 3)]
    """
    # ===traverse all edges===
    # Solution 1:
    # for node, nbr_dict in directed_graph.adjacency():
    #     for nbr, edge_attr in nbr_dict.items():
    #         if 'influence' not in edge_attr:
    #             pass

    # Solution 2:
    for u, v, influence in directed_graph.edges(data='influence'):
        if influence is None:
            # noinspection PyCallingNonCallable
            out_degree = directed_graph.out_degree(u)
            out_degree_sum = 0
            for src, dst in directed_graph.in_edges(v):
                # noinspection PyCallingNonCallable
                out_degree_sum += directed_graph.out_degree(src)
            directed_graph[u][v]['influence'] = out_degree / out_degree_sum
        elif influence > 1:
            raise Exception("Edge error: The influence of edge({}, {}) cannot be larger than 1.".format(u, v))

    # perform diffusion
    seeds_duplicate = copy.deepcopy(seeds)
    if steps <= 0:
        # perform diffusion until no more nodes can be activated
        return _diffuse_all(directed_graph, seeds_duplicate)
    # perform diffusion for at most "steps" rounds only
    return _diffuse_k_rounds(directed_graph, seeds_duplicate, steps)


def _diffuse_all(graph, seeds):
    layer_i_nodes = [[i for i in seeds]]
    while True:
        len_old = len(seeds)
        seeds, activated_nodes_of_this_round = _diffuse_one_round(graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
        if len(seeds) == len_old:
            break
    return layer_i_nodes


def _diffuse_k_rounds(graph, seeds, steps):
    layer_i_nodes = [[i for i in seeds]]
    while steps > 0 and len(seeds) < len(graph):
        len_old = len(seeds)
        seeds, activated_nodes_of_this_round = _diffuse_one_round(graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
        if len(seeds) == len_old:
            break
        steps -= 1
    return layer_i_nodes


def _diffuse_one_round(graph, seeds):
    activated_nodes_of_this_round = set()
    for seed in seeds:
        neighbor_list = graph.successors(seed)
        for nb in neighbor_list:
            if nb in seeds:
                continue
            active_nb = list(set(graph.predecessors(nb)).intersection(set(seeds)))
            if _influence_sum(graph, active_nb, nb) >= graph.node[nb]['threshold']:
                activated_nodes_of_this_round.add(nb)
    seeds.extend(list(activated_nodes_of_this_round))
    return seeds, list(activated_nodes_of_this_round)


def _influence_sum(graph, from_list, to):
    influence_sum = 0.0
    for f in from_list:
        influence_sum += graph[f][to]['influence']
    return influence_sum
