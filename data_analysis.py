#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import igraph
import networkx as nx
import plotly.graph_objs as go
from plotly.offline import iplot


def read_data(file):
    dataset = []
    with open(file) as fr:
        for line in fr.readlines():
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
    # start = datetime.now()
    edges_data = read_data('OF_one-mode_weightedmsg_Newman.txt')
    # end = datetime.now()
    # print("Read Data cost: {}s".format(end - start))
    # undirected_graph = nx.Graph()
    # undirected_graph.add_edges_from(edges_data)
    #
    # nx.draw(undirected_graph, with_labels=True, font_weight='bold', node_color='y', )
    # plt.show()

    draw_3d(edges_data)

    # start = datetime.now()
    # print(find_optimal(undirected_graph))
    # end = datetime.now()
    # print("Find optimal cost: {}s".format(end - start))
