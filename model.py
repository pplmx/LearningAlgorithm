#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy

import networkx as nx

__all__ = ['linear_threshold']


# -------------------------------------------------------------------------
#  Some Famous Diffusion Models
# -------------------------------------------------------------------------

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
    """
    if type(graph) == nx.MultiGraph or type(graph) == nx.MultiDiGraph:
        raise Exception("linear_threshold() is not defined for graphs with multiedges.")

    # make sure the seeds are in the graph
    for seed in seeds:
        if seed not in graph.nodes():
            raise Exception("seed", seed, "is not in graph")

    # change to directed graph
    if not graph.is_directed():
        # directed_graph = G.to_directed()
        directed_graph = nx.DiGraph(graph)
    else:
        directed_graph = copy.deepcopy(graph)

    # init thresholds
    """
    >>> list(graph.nodes)
    [0, 1, 2]
    >>> list(graph)
    [0, 1, 2]
    """
    for i in list(directed_graph.nodes):
        if 'threshold' not in directed_graph.nodes[i]:
            directed_graph.nodes[i]['threshold'] = 0.5
        elif directed_graph.nodes[i]['threshold'] > 1:
            raise Exception("node threshold:", directed_graph.nodes[i]['threshold'], "cannot be larger than 1")

    # init influences

    # in_deg_all = directed_graph.in_degree()        #获取所有节点的入度
    # noinspection PyCallingNonCallable
    out_degree_list = list(directed_graph.out_degree(list(directed_graph)))  # 获取所有节点的出度
    in_edge_list = directed_graph.in_edges  # 获取所有的入边
    """
    >>> [e for e in graph.edges]
    [(0, 1), (1, 2), (2, 3)]
    """
    # =========traverse all edges=========
    # Solution 1:
    for node, nbr_dict in directed_graph.adjacency():
        for nbr, edge_attr in nbr_dict.items():
            if 'influence' not in edge_attr:
                pass

    # Solution 2:
    for u, v, influence in directed_graph.edges(data='influence'):
        if influence is None:
            out_degree = directed_graph.out_degree(u)
            out_degree_sum = None

            directed_graph[u][v]['influence'] = out_degree / out_degree_sum
        elif influence > 1:
            raise Exception("Edge error: The influence of edge({}, {}) cannot be larger than 1.".format(u, v))

    # for directed graph, directed_graph.edges only contains out edges without in edges
    for edge in directed_graph.edges:
        if 'influence' not in directed_graph[edge[0]][edge[1]]:
            out_degree = out_degree_list[edge[0]]  # 获取节点edge[0]的出度
            # in_edges = in_edge_list._adjdict[edge[1]]  # 获取节点edge[1]的所有的入边
            # in_edges = directed_graph.adj[edge[1]]
            in_edges = directed_graph.in_edges(edge[1])  # 获取节点edge[1]的所有的入边
            edges_dict = dict(in_edges)
            in_edges_all = list(edges_dict.keys())  # 获取节点edge[1]的所有入边节点并存入列表
            out_degree_sum = 0
            for i in in_edges_all:  # 求节点e[1]所有入边节点的出度和
                out_degree_sum += out_degree_list[i]
            directed_graph[edge[0]][edge[1]]['influence'] = out_degree / out_degree_sum
        elif directed_graph[edge[0]][edge[1]]['influence'] > 1:
            raise Exception("edge influence:", directed_graph[edge[0]][edge[1]]['influence'], "cannot be larger than 1")

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