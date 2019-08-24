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
      layer_i_nodes[0]: the origin seeds
      layer_i_nodes[k]: the activated nodes what are activated at the kth diffusion step
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

    # make sure the seeds are in the graph and unique
    seeds = list(set(seeds))
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
            # the sum of the out-degree of all in-edge nodes of v
            out_degree_sum = 0
            for src, dst in directed_graph.in_edges(v):
                # noinspection PyCallingNonCallable
                out_degree_sum += directed_graph.out_degree(src)
            directed_graph[u][v]['influence'] = out_degree / out_degree_sum
        elif influence > 1:
            raise Exception("Edge error: The influence of edge({}, {}) cannot be larger than 1.".format(u, v))

    # perform diffusion
    seeds_duplicate = copy.deepcopy(seeds)
    return diffuse(directed_graph, seeds_duplicate, steps)


def diffuse(directed_graph, seeds, steps=0):
    if steps <= 0:
        # perform diffusion until no more nodes can be activated
        return diffuse_all(directed_graph, seeds)
    # perform diffusion for at most "steps" rounds only
    return diffuse_k_rounds(directed_graph, seeds, steps)


def diffuse_all(directed_graph, seeds):
    """
        To activate all nodes
    :param directed_graph:
    :param seeds:
    :return:
    """
    layer_i_nodes = [[i for i in seeds]]
    while len(seeds) < len(directed_graph):
        seeds, activated_nodes_of_this_round = diffuse_one_round(directed_graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
    return layer_i_nodes


def diffuse_k_rounds(directed_graph, seeds, steps):
    """
            To activate all seeds' successor {steps} times
    :param directed_graph:
    :param seeds:
    :param steps:
    :return:
    """
    layer_i_nodes = [[i for i in seeds]]
    while steps > 0 and len(seeds) < len(directed_graph):
        origin_len = len(seeds)
        seeds, activated_nodes_of_this_round = diffuse_one_round(directed_graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
        # if all nodes had been diffused, break the loop
        if len(seeds) == origin_len:
            break
        steps -= 1
    return layer_i_nodes


def diffuse_one_round(directed_graph, seeds):
    """
        To activate all seeds' successor once
    :param directed_graph:
    :param seeds:
    :return:
    """
    activated_nodes_of_this_round = set()
    for seed in seeds:
        # get all successors of the seed (from seed to successor)
        successor_list = directed_graph.successors(seed)
        for successor in successor_list:
            if successor in seeds:
                continue
            # if successor is not in seed, to check whether it can be activated (diffused)
            if is_can_be_activated(directed_graph, successor):
                activated_nodes_of_this_round.add(successor)
    # add the successors what are activated in this round to the seeds
    # next round, use the new seeds what are extended to diffuse
    seeds.extend(list(activated_nodes_of_this_round))
    return seeds, list(activated_nodes_of_this_round)


def is_can_be_activated(directed_graph, node):
    """
        ######## To determine if a node can be activated ########
        if node's all in-edges' influence_sum >= node's threshold,
        it's can be activated (diffused).
    :param directed_graph:
    :param node:
    :return:
    """
    influence_factor = 0
    for u, v, influence in directed_graph.in_edges(node, data='influence'):
        influence_factor += influence
    # calculate the sum of the weights of all the in degrees of node
    # directed_graph.in_degree(node, weight="influence")
    # calculate the sum of the weights of all the out degrees of node
    # directed_graph.out_degree(node, weight="influence")
    if influence_factor >= directed_graph.nodes[node]['threshold']:
        return True
    return False


if __name__ == '__main__':
    dg = nx.DiGraph()
    dg.add_weighted_edges_from([(1, 2, 0.5), (1, 3, 1.1), (4, 1, 2.3), (4, 2, 0.9)], weight='influence')
    influence_factor_ = 0
    for u_, v_, influence_ in dg.in_edges(3, data='influence'):
        influence_factor_ += influence_
    # The following values are the same
    print(influence_factor_)
    # noinspection PyCallingNonCallable
    print(dg.in_degree(3, weight="influence"))
