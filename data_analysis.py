#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

import networkx as nx

from find_optimal import find_optimal


def read_data(file):
    dataset = []
    with open(file) as fr:
        for line in fr.readlines():
            tmp = line.split()
            dataset.append((tmp[0], tmp[1]))
    return dataset


if __name__ == '__main__':
    time.no
    data = read_data('OF_one-mode_weightedmsg_Newman.txt')
    undirected_graph = nx.Graph()
    undirected_graph.add_edges_from(data)
    print(find_optimal(undirected_graph))
