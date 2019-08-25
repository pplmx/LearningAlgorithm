#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

from numpy import random

from LT_model import linear_threshold


def find_optimal(graph):
    minimal_dominating_set = set()
    degree_list = list(graph.degree)
    # store the node whose degree is zero
    degree_0_node_list = [node for node, deg in degree_list if deg == 0]
    # store the node who has a neighbor whose degree is 1
    degree_1_node_nbr_list = [graph.neighbors(node)[0] for node, deg in degree_list if deg == 1]


def _linear_clime(graph, k):  # 参数k-表示要获取的子节点的个数
    all_node_list = graph.nodes()  # 获取图中所有节点数
    seed_node_list = []  # 该列表存储选取的子节点集
    layers_max = None
    for m in range(k):
        all_nodes = list(all_node_list)  # 将所有的节点存储在all_nodes列表里
        layers_activate = []  # 存储每个节点的激活节点列表
        lengths = []  # 存储每个节点的激活列表长度
        data_list = []
        for i in all_nodes:  # 遍历所有的节点，分别求出每个节点对应的激活节点集以及激活节点集的长度
            data_list.append(i)
            data_test = seed_node_list + [i]
            layers = linear_threshold(graph, data_test)
            del layers[-1]
            length = 0
            layer_data = []
            for j in range(len(layers)):
                length = length + len(layers[j])
                layer_data = layer_data + layers[j]
            length_s = length - len(layers[0])
            for s in range(len(layers[0])):
                del layer_data[0]
            layers_activate.append(layer_data)
            lengths.append(length_s)
        # length_max = max(lengths)  # 获取激活节点最多的节点数
        layers_max = layers_activate[lengths.index(max(lengths))]  # 获取被激活节点数最多的列表
        seed_node_list.append(data_list[lengths.index(max(lengths))])  # 获取被激活节点最多的子节点
        for i in all_nodes:  # 该循环是删除所有节点中seed_nodes节点集
            if i in seed_node_list:
                del all_nodes[all_nodes.index(i)]
        all_node_list = all_nodes
    return seed_node_list, layers_max  # 返回值是贪心算法求得的子节点集和该子节点集激活的最大节点集


def quick_sort4tuple_list(unsorted_list, idx=0):
    """
        unsorted_list e.g.:
                [(1, 3), (5, 9), (2, 1), (4, 14)]
                [(1, 3, 12), (5, 9, 1), (2, 1, 343), (4, 14, 0)]
    :param unsorted_list:
    :param idx:
    :return:
    """
    data_len = len(unsorted_list)
    if data_len <= 1:
        return unsorted_list
    rand_val = random.randint(data_len)
    mid_tuple = unsorted_list[rand_val]
    del unsorted_list[rand_val]
    print(mid_tuple)
    less = [i for i in unsorted_list if i[idx] <= mid_tuple[idx]]
    print("less: ", less)
    greater = [i for i in unsorted_list if i[idx] > mid_tuple[idx]]
    print("greater: ", greater)
    return quick_sort4tuple_list(less) + [mid_tuple] + quick_sort4tuple_list(greater)


# 测试算法
if __name__ == '__main__':
    # dataset = []
    # f = open("Wiki-Vote.txt")
    # data = f.read()
    # rows = data.split('\n')
    # for row in rows:
    #     split_row = row.split('\t')
    #     name = (int(split_row[0]), int(split_row[1]))
    #     dataset.append(name)
    # G = nx.DiGraph()
    # G.add_edges_from(dataset)  # 根据数据集创建有向图
    #
    # n = input('Please input the number of seeds: k=')
    # k = int(n)
    # seed_nodes, layers_max = _linear_clime(G, k)  # 调用贪心算法获取节点子集和节点子集的最大激活节点集
    #
    # print(seed_nodes)
    # print(layers_max)
    li = [(1, 3, 12), (5, 9, 1), (2, 1, 343), (4, 14, 0)]
    print(quick_sort4tuple_list(li, 1))
    pass
