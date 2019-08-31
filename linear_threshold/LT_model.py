#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

import networkx as nx


# -----------------------------------
#  Diffusion Models
# -----------------------------------

class LinearThresholdModel:
    def __init__(self, graph, seeds, steps=0):
        self.graph = graph
        self.seeds = seeds
        self.steps = steps


def linear_threshold(graph, seeds: set, steps=0):
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
    if the graph is a directed graph
        1. Each node is supposed to have an attribute "threshold".  If not, the
           default value is given (0.5).
        2. Each edge is supposed to have an attribute "influence".  If not, the
           default value is given (out_deg / out_deg_sum)
        3. edge(u, v)'s influence = u's out_deg / u's all adjacency in_edges' nodes' out_deg_sum
    """
    if type(graph) == nx.MultiGraph or type(graph) == nx.MultiDiGraph:
        raise Exception("linear_threshold() is not defined for graphs with multi-edges.")

    # is directed or not
    if graph.is_directed():
        directed_graph = copy.deepcopy(graph)

        # make sure the seeds are in the graph and unique
        for seed in seeds:
            if seed not in directed_graph.nodes():
                raise Exception("seed ", seed, " is not in directed graph")

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
        for u, v, influence in directed_graph.edges(data='influence'):
            if influence is None:
                # ========== influence = out_degree / out_degree_sum ==========
                # # noinspection PyCallingNonCallable
                # out_degree = directed_graph.out_degree(u)
                # # the sum of the out-degree of all in-edge nodes of v
                # out_degree_sum = 0
                # for src, dst in directed_graph.in_edges(v):
                #     # noinspection PyCallingNonCallable
                #     out_degree_sum += directed_graph.out_degree(src)
                # directed_graph[u][v]['influence'] = out_degree / out_degree_sum

                # ========== influence = 1 / in_degree ==========
                # noinspection PyCallingNonCallable
                directed_graph[u][v]['influence'] = 1 / directed_graph.in_degree(v)
            elif influence > 1:
                raise Exception("Edge error: The influence of edge({}, {}) cannot be larger than 1.".format(u, v))

        # perform diffusion
        seeds_duplicate = copy.deepcopy(seeds)
        return diffuse(directed_graph, seeds_duplicate, steps)
    else:
        undirected_graph = copy.deepcopy(graph)

        # make sure the seeds are in the graph and unique
        for seed in seeds:
            if seed not in undirected_graph.nodes():
                raise Exception("seed ", seed, " is not in undirected graph")

        # perform diffusion
        seeds_duplicate = copy.deepcopy(seeds)
        return diffuse(undirected_graph, seeds_duplicate, steps)


def diffuse(graph, seeds: set, steps=0):
    if steps <= 0:
        # perform diffusion until no more nodes can be activated
        return diffuse_all(graph, seeds)
    # perform diffusion for at most "steps" rounds only
    return diffuse_k_rounds(graph, seeds, steps)


def diffuse_all(graph, seeds: set):
    """
        To activate all nodes
    :param graph:
    :param seeds:
    :return:
    """
    layer_i_nodes = [[i for i in seeds]]
    while len(seeds) < len(graph):
        seeds, activated_nodes_of_this_round = diffuse_one_round(graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
    return layer_i_nodes


def diffuse_k_rounds(graph, seeds: set, steps=1):
    """
            To activate all seeds' successors[directed_graph] or neighbors[undirected_graph] {steps} times
    :param graph:
    :param seeds:
    :param steps:
    :return:
    """
    layer_i_nodes = [[i for i in seeds]]
    while steps > 0 and len(seeds) < len(graph):
        origin_len = len(seeds)
        seeds, activated_nodes_of_this_round = diffuse_one_round(graph, seeds)
        layer_i_nodes.append(activated_nodes_of_this_round)
        # if all nodes had been diffused, break the loop
        if len(seeds) == origin_len:
            break
        steps -= 1
    return layer_i_nodes


def diffuse_one_round(graph, origin_seeds: set):
    """
        To activate all seeds' successors[directed_graph] or neighbors[undirected_graph] once
    :param graph:
    :param origin_seeds:
    :return:
    """
    next_seeds = set(origin_seeds)
    activated_nodes_of_this_round = set()
    if graph.is_directed():
        for seed in origin_seeds:
            # get all successors of the seed (from seed to successor)
            successor_list = graph.successors(seed)
            for successor in successor_list:
                if successor in origin_seeds:
                    continue
                # if successor is not in seed, to check whether it can be activated (diffused)
                if is_can_be_activated(graph, successor):
                    activated_nodes_of_this_round.add(successor)

        # delete seeds from activated nodes in this round
        for seed in origin_seeds:
            if seed in activated_nodes_of_this_round:
                activated_nodes_of_this_round.remove(seed)

        # add the successors what are activated in this round to the seeds
        # next round, use the new seeds what are extended to diffuse
        next_seeds |= activated_nodes_of_this_round
    else:
        for seed in origin_seeds:
            # get all neighbors of the seed
            # (The following two expressions are equivalent, but the latter is recommended.)
            # nbr_list = graph.neighbors(seed)
            nbr_list = graph[seed]
            activated_nodes_of_this_round |= set(nbr_list)

        # ===== To increase the rate of diffuse, comment the following code =====
        # delete seeds from activated nodes in this round
        # for seed in seeds:
        #     if seed in activated_nodes_of_this_round:
        #         activated_nodes_of_this_round.remove(seed)

        # add the neighbors what are activated in this round to the seeds
        # next round, use the new seeds what are extended to diffuse
        next_seeds |= activated_nodes_of_this_round

    return next_seeds, list(activated_nodes_of_this_round)


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
