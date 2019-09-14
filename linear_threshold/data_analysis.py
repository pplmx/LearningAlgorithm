#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import igraph
import networkx as nx
import plotly.graph_objs as go
from plotly.offline import iplot

from linear_threshold.LT_model import LinearThresholdModel


def read_data(file):
    dataset = []
    with open(file) as fr:
        for line in fr.readlines():
            if line.startswith("#"):
                continue
            tmp = line.split()
            dataset.append((int(tmp[0]), int(tmp[1])))
    return dataset


def draw_3d(edges_list):
    # get the Graph object from edges
    ig = igraph.Graph(edges_list, directed=False)
    udg = nx.Graph()
    udg.add_edges_from(edges_list)
    # Get the node positions, set by the Kamada-Kawai layout for 3D graphs
    # layout is a list of three elements lists (the coordinates of nodes):
    layout = ig.layout('kk_3d')
    nodes_num = ig.vcount()
    edges_num = ig.ecount()

    node_name = [k for k in list(udg)]
    node_color = [k for k in list(udg)]

    x_node = [layout[k][0] for k in list(udg)]  # x-coordinates of nodes
    y_node = [layout[k][1] for k in list(udg)]  # y-coordinates
    z_node = [layout[k][2] for k in list(udg)]  # z-coordinates
    x_edge = []
    y_edge = []
    z_edge = []
    for edge in edges_list:
        x_edge += [layout[edge[0]][0], layout[edge[1]][0], None]  # x-coordinates of edge ends
        y_edge += [layout[edge[0]][1], layout[edge[1]][1], None]
        z_edge += [layout[edge[0]][2], layout[edge[1]][2], None]

    trace1 = go.Scatter3d(x=x_edge,
                          y=y_edge,
                          z=z_edge,
                          mode='lines',
                          line=dict(color='rgb(125,125,125)', width=1),
                          hoverinfo='none'
                          )

    trace2 = go.Scatter3d(x=x_node,
                          y=y_node,
                          z=z_node,
                          mode='markers',
                          name='actors',
                          marker=dict(symbol='circle',
                                      size=6,
                                      color=node_color,
                                      colorscale='Viridis',
                                      line=dict(color='rgb(50,50,50)', width=0.5)
                                      ),
                          text=node_name,
                          hoverinfo='text'
                          )

    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

    layout = go.Layout(
        title="3D visualization",
        width=1000,
        height=1000,
        showlegend=False,
        scene=dict(
            xaxis=dict(axis),
            yaxis=dict(axis),
            zaxis=dict(axis),
        ),
        margin=dict(
            t=100
        ),
        hovermode='closest',
    )

    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=layout)

    # py.iplot(fig, filename='Les-Miserables')
    iplot(fig, filename='3D undirected graph')


if __name__ == '__main__':
    mds_start = datetime.now()
    edges_data = read_data('../data/CA-GrQc.txt')
    mds_end = datetime.now()
    print("Read Data cost: {}s".format(mds_end - mds_start))

    mds_start = datetime.now()
    graph = nx.Graph()
    graph.add_edges_from(edges_data)
    mds_end = datetime.now()
    print("Build graph by networkx cost: {}s".format(mds_end - mds_start))

    # custom_ego_list = [(1, 5), (1, 13), (1, 16), (1, 28),
    #                    (5, 20), (5, 21), (5, 22), (5, 23), (5, 24), (5, 25), (5, 26), (5, 27),
    #                    (13, 2), (13, 3), (13, 4), (13, 6), (13, 7), (13, 8), (13, 9), (13, 10), (13, 11), (13, 12),
    #                    (16, 29), (16, 30), (16, 31), (16, 32), (16, 33), (16, 34),
    #                    (28, 14), (28, 15), (28, 17), (28, 18), (28, 19)
    #                    ]
    # draw_3d(custom_ego_list)

    lt_model = LinearThresholdModel(graph)
    graph = lt_model.get_graph()
    mds_start = datetime.now()
    mds = lt_model.find_mds_basing_max_degree()
    mds_end = datetime.now()

    mbs_start = datetime.now()
    mbs = lt_model.find_mbs()
    mbs_end = datetime.now()

    print("Find mds cost: {}s".format(mds_end - mds_start))
    print("The minimal dominating set: {}".format(mds))
    print("Its length: {}".format(len(mds)))

    print("Find mbs cost: {}s".format(mbs_end - mbs_start))
    print("The minimal burning set: {}".format(mbs))
    print("Its length: {}".format(len(mbs)))

    # lt_model.set_burning_seq([100, 334])
    # print(lt_model.link_the_fire())
    # print(len(graph))

    # mds = {2, 532, 539, 541, 42, 563, 90, 612, 660, 662, 674, 677, 172, 686, 687, 690, 698, 701, 708, 711, 713, 719, 722, 728, 730, 731, 732, 740, 742, 748, 752, 753, 246, 761, 763, 773, 261, 282, 796, 799, 802, 803, 804, 807, 810, 811, 812, 813, 817, 819, 312, 825, 826, 830, 834, 325, 841, 330, 847, 850, 854, 857, 862, 869, 870, 872, 362, 875, 363, 373, 375, 893, 388, 400, 436, 451, 472}
    # mds_facebook_ego = {0, 107, 3980, 3437, 686, 1684, 1912, 698, 348, 414}
    # mds = {1, 2, 129, 13, 783, 400, 658, 148, 149, 790, 532, 282, 28, 796, 798, 159, 799, 803, 164, 810, 686, 53, 695, 186, 67, 451, 325, 580, 201, 330, 205, 720, 337, 722, 849, 593, 86, 728, 217, 472, 91, 220, 732, 228, 742, 748, 495, 751, 752, 626, 373, 246, 375}
    #
    # lt_model.set_seeds(mds)
    # layer_i_nodes = lt_model.diffuse()
    # print("The length of layer_i_nodes: {}.".format(len(layer_i_nodes)))
