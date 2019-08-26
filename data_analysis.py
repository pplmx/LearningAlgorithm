#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx


def read_data(file):
    dataset = []
    with open(file) as fr:
        for line in fr.readlines():
            tmp = line.split()
            dataset.append((tmp[0], tmp[1]))
    return dataset


if __name__ == '__main__':
    start = datetime.now()
    data = read_data('OF_one-mode_weightedmsg_Newman.txt')
    end = datetime.now()
    print("Read Data cost: {}s".format(end - start))
    undirected_graph = nx.Graph()
    undirected_graph.add_edges_from(data)

    nx.draw(undirected_graph, with_labels=True, font_weight='bold', node_color='y', )
    plt.show()

    # start = datetime.now()
    # print(find_optimal(undirected_graph))
    # end = datetime.now()
    # print("Find optimal cost: {}s".format(end - start))
