import unittest

import networkx

from LT_model import linear_threshold


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.dg = networkx.DiGraph()
        self.dg.add_edge(1, 2, influence=.5)
        self.dg.add_edge(2, 1, influence=.5)
        self.dg.add_edge(1, 3, influence=.2)
        self.dg.add_edge(3, 1, influence=.2)
        self.dg.add_edge(2, 3, influence=.3)
        self.dg.add_edge(2, 4, influence=.5)
        self.dg.add_edge(3, 4, influence=.1)
        self.dg.add_edge(3, 5, influence=.2)
        self.dg.add_edge(4, 5, influence=.2)
        self.dg.add_edge(5, 6, influence=.6)
        self.dg.add_edge(6, 5, influence=.6)
        self.dg.add_edge(6, 4, influence=.3)
        self.dg.add_edge(6, 2, influence=.4)
        self.dg.nodes[2]['threshold'] = .4
        self.dg.nodes[3]['threshold'] = .4
        self.dg.nodes[4]['threshold'] = .55
        self.dg.nodes[5]['threshold'] = .5
        self.dg.nodes[6]['threshold'] = .3

    def test_linear_threshold_directed_graph(self):
        print(linear_threshold(self.dg, [1]))
        print(linear_threshold(self.dg, [1, 4]))
        print(linear_threshold(self.dg, [1, 6]))

    def test_linear_threshold_directed_graph_with_step(self):
        print(linear_threshold(self.dg, [1], 1))
        print(linear_threshold(self.dg, [1], 2))

    def test_linear_threshold_undirected_graph(self):
        self.dg = networkx.Graph()
        self.dg.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)])

        print(linear_threshold(self.dg, [1]))
        print(linear_threshold(self.dg, [1, 4]))
        print(linear_threshold(self.dg, [1, 2]))


if __name__ == '__main__':
    unittest.main()
