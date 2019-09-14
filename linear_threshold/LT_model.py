#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

import networkx as nx

# -----------------------------------
#  Diffusion Models
# -----------------------------------

"""
Parameters
----------
graph : networkx graph
    The number of nodes.
seeds: set of nodes
    The seed nodes of the graph
burning_seq: list
    burning sequence, it's ordered.
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


class LinearThresholdModel:
    def __init__(self, graph, seeds: set = None, burning_seq: list = None, steps: int = 0):
        self.__graph = graph
        self.__seeds = seeds
        self.__burning_seq = burning_seq
        self.__steps = steps
        self.__init_model()

    def __init_model(self):
        if type(self.__graph) == nx.MultiGraph or type(self.__graph) == nx.MultiDiGraph:
            raise Exception("LinearThresholdModel is not defined for graphs with multi-edges.")

        # is directed or not
        if self.__graph.is_directed():
            directed_graph = copy.deepcopy(self.__graph)

            # >>>>>>>>>> init thresholds <<<<<<<<<<
            init_threshold4directed_graph(directed_graph)
            # >>>>>>>>>> init influences <<<<<<<<<<
            init_influence4directed_graph(directed_graph)

            self.__graph = copy.deepcopy(directed_graph)

    def diffuse(self):
        if self.__steps <= 0:
            # perform diffusion until no more nodes can be activated
            return self.__diffuse_all(self.__seeds)
        # perform diffusion for at most "steps" rounds only
        return self.__diffuse_k_rounds(self.__seeds, self.__steps)

    def link_the_fire(self):
        burned_set = set()
        burning_set = set()
        for i in self.__burning_seq:
            if i not in burned_set:
                burning_set.add(i)
                self.__fire(burning_set, burned_set)
        return len(burned_set | burning_set)

    def __fire(self, burning_set, burned_set):
        for i in copy.deepcopy(burning_set):
            burned_set.add(i)
            burning_set.remove(i)
            burning_set |= set(self.__graph[i]) - burned_set

    def find_mds_basing_max_degree(self):
        """
            find the minimal dominating set
        :return:
        """
        minimal_dominating_set = set()
        dominated_set = set()

        if self.__graph.is_directed():
            # Right now, we handle nothing to directed graph.
            in_degree_list = sorted(self.__graph.in_dgree, key=lambda x: (x[1], x[0]))
            pass

        # graph: [(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)]
        # list(graph.degree)
        # [(1, 2), (2, 2), (3, 4), (4, 3), (5, 3), (6, 2)]
        # after sort
        # [(1, 2), (2, 2), (6, 2), (4, 3), (5, 3), (3, 4)]
        degree_list = sorted(list(self.__graph.degree), key=lambda x: (x[1], x[0]))

        # store the node whose degree is zero
        degree_0_node_set = set()
        # store the node who has a neighbor whose degree is 1
        degree_1_node_nbr_set = set()

        for idx, val in enumerate(degree_list):
            if val[1] == 0:
                degree_0_node_set.add(val[0])
            elif val[1] == 1:
                # because the degree is 1, so node's neighbor is unique.
                neighbor_of_current_node = list(self.__graph[val[0]])[0]

                # update dominated_set, i.e. the nodes whose are dominated by minimal_dominating_set
                dominated_set |= set(self.__graph[neighbor_of_current_node])
                degree_1_node_nbr_set.add(neighbor_of_current_node)
            else:
                # remove the nodes whose degree is 0 or 1
                # to reduce the potential redundant loop
                degree_list = degree_list[idx:]
                break
        minimal_dominating_set |= degree_0_node_set | degree_1_node_nbr_set

        for node, deg in degree_list[::-1]:
            if node not in minimal_dominating_set and node not in dominated_set:
                # update minimal dominating set and dominated set
                minimal_dominating_set.add(node)
                dominated_set |= set(self.__graph[node])
        return minimal_dominating_set

    def find_mbs(self):
        """
            find the minimal burning sequence
        :return:
        """
        minimal_burning_sequence_list = []
        burned_set = set()
        burning_set = set()
        # Get a list reversely ordered by degree. e.g. [(2, 3), (4, 2), (3, 2), (1, 1)]
        degree_list = sorted(list(self.__graph.degree), key=lambda x: (x[1], x[0]), reverse=True)
        for idx, val in enumerate(degree_list):
            if val[0] not in burned_set and val[0] not in burning_set:
                minimal_burning_sequence_list.append(val[0])
                burned_set.add(val[0])
                burning_set |= set(self.__graph[val[0]]) - burned_set
                if idx > 0:
                    # remove the nodes who are burned on last round from burning_set
                    # meanwhile, add them to burned_set
                    burning_set -= set(self.__graph[degree_list[idx - 1][0]])
                    burned_set |= set(self.__graph[degree_list[idx - 1][0]])
        return minimal_burning_sequence_list

    def find_mds_basing_dfs(self, source=None):
        minimal_dominating_set = set()

        next_pre_dict = nx.dfs_predecessors(self.__graph, source)
        successor_list = list(next_pre_dict.keys())
        # The node set whose are dominated(covered) by minimal dominating set
        covered_set = set()
        for node in self.__graph:
            # if itself and its predecessor are both not in minimal_dominating_set
            # meanwhile, itself is not in covered_set
            if node not in successor_list:
                continue
            predecessor = next_pre_dict[node]
            if node not in minimal_dominating_set and node not in covered_set and predecessor not in minimal_dominating_set:
                minimal_dominating_set.add(predecessor)
                # get predecessor's neighbors, i.e. the nodes whose are covered by predecessor
                covered_set |= set(self.__graph[predecessor])
        return minimal_dominating_set

    def __diffuse_all(self, seeds: set):
        """
            To activate all nodes
        :param seeds:
        :return: layer_i_nodes
        """

        next_seeds = set(seeds)
        layer_i_nodes = [[i for i in next_seeds]]
        while len(next_seeds) < len(self.__graph):
            next_seeds, activated_nodes_of_this_round = self.__diffuse_one_round(next_seeds)
            layer_i_nodes.append(activated_nodes_of_this_round)
        return layer_i_nodes

    def __diffuse_k_rounds(self, seeds: set, steps=1):
        """
                To activate all seeds' successors[directed_graph] or neighbors[undirected_graph] {steps} times
        :param seeds:
        :param steps:
        :return: layer_i_nodes
        """
        next_seeds = set(seeds)
        layer_i_nodes = [[i for i in next_seeds]]
        while steps > 0 and len(next_seeds) < len(self.__graph):
            origin_len = len(next_seeds)
            next_seeds, activated_nodes_of_this_round = self.__diffuse_one_round(next_seeds)
            layer_i_nodes.append(activated_nodes_of_this_round)
            # if all nodes had been diffused, break the loop
            if len(next_seeds) == origin_len:
                break
            steps -= 1
        return layer_i_nodes

    def __diffuse_one_round(self, origin_seeds: set):
        """
            To activate all seeds' successors[directed_graph] or neighbors[undirected_graph] once
        :param origin_seeds:
        :return: (next_seeds, activated_nodes_of_this_round)
        """
        next_seeds = set(origin_seeds)
        activated_nodes_of_this_round = set()
        if self.__graph.is_directed():
            for seed in origin_seeds:
                # get all successors of the seed (from seed to successor)
                successor_list = self.__graph.successors(seed)
                for successor in successor_list:
                    if successor in origin_seeds:
                        continue
                    # if successor is not in seed, to check whether it can be activated (diffused)
                    if self.__is_can_be_activated(successor):
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
                nbr_list = self.__graph[seed]
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

    def __is_can_be_activated(self, node):
        """
            ######## To determine if a node can be activated ########
            if node's all in-edges' influence_sum >= node's threshold,
            it's can be activated (diffused).
        :param graph:
        :param node:
        :return:
        """
        if not self.__graph.is_directed():
            raise Exception("Graph Error: The graph must be the directed graph.")
        influence_factor = 0
        for u, v, influence in self.__graph.in_edges(node, data='influence'):
            influence_factor += influence
        # calculate the sum of the weights of all the in degrees of node
        # directed_graph.in_degree(node, weight="influence")
        # calculate the sum of the weights of all the out degrees of node
        # directed_graph.out_degree(node, weight="influence")
        if influence_factor >= self.__graph.nodes[node]['threshold']:
            return True
        return False

    def is_seeds_in_graph(self):
        # make sure the seeds are in the graph and unique
        node_set = set(self.__graph)
        if not self.__seeds.issubset(node_set):
            for seed in self.__seeds:
                if seed not in node_set:
                    raise Exception("seed ", seed, " is not in graph")

    def set_seeds(self, seeds):
        self.__seeds = seeds

    def set_steps(self, steps):
        self.__steps = steps

    def set_burning_seq(self, burning_seq):
        self.__burning_seq = burning_seq

    def get_graph(self):
        return self.__graph


def init_threshold4directed_graph(directed_graph):
    """
    >> list(graph.nodes)
    [0, 1, 2]
    >> list(graph)
    [0, 1, 2]
    """
    for i, threshold in directed_graph.nodes(data='threshold'):
        if threshold is None:
            directed_graph.nodes[i]['threshold'] = 0.5
        elif threshold > 1:
            raise Exception("Node error: The threshold of node-{} cannot be larger than 1.".format(i))


def init_influence4directed_graph(directed_graph):
    # >>>>>>>>>> init influences <<<<<<<<<<
    """
    >> [e for e in graph.edges]
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
