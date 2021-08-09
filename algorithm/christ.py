import networkx as nx
from itertools import combinations, product
import numpy as np
from networkx.algorithms.bipartite import minimum_weight_full_matching as mwfm
from .utils import distances_table, get_distance
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)


def create_graph(df, df_dist) -> nx.Graph():
    G = nx.Graph()
    G.add_nodes_from(list(df.index))
    edge_list = []
    for index, row in df_dist.iterrows():
        edge_list.append((row.city1, row.city2, {'weight': row.dist}))
    G.add_edges_from(edge_list)
    return G


def optimal_matching(nodes, df_dist):
    # algorithm can't be applied on odd number of vertices
    choices = {}
    if len(nodes) % 2 != 0:
        raise ValueError
    for nodes_set_1 in combinations(nodes, int(len(nodes) / 2)):
        nodes_set_2 = [node for node in nodes if node not in nodes_set_1]
        bipart_graph = nx.Graph()
        bipart_graph.add_nodes_from(nodes_set_1, bipartite=0)
        bipart_graph.add_nodes_from(nodes_set_2, bipartite=1)
        for node1, node2 in product(nodes_set_1, nodes_set_2):
            bipart_graph.add_edge(node1, node2, weight=get_distance(node1, node2, df_dist))
        mwm = mwfm(bipart_graph, weight='weight')
        tmp_nodes = []
        final_mwm = []
        for k in mwm.keys():
            if k not in tmp_nodes:
                final_mwm.append([k, mwm[k]])
                tmp_nodes.extend([k, mwm[k]])
        dist = sum([get_distance(edge[0], edge[1], df_dist) for edge in final_mwm])
        choices.update({dist: final_mwm})
    minimal = min(choices.keys())
    return choices[minimal]


class ChristAlgorithm:
    """
    Class constructor uses DataFrame as initial data.
    Index = cities
    Columns = longitude, latitude
    """

    def __init__(self, df):

        self.logger = logging.getLogger('main_flow')
        self.logger.setLevel('INFO')

        self.df = df
        self.df_dist = distances_table(df)
        self.G = create_graph(self.df, self.df_dist)

        self._complexity = 0
        self.subG = None

        # minimum spanning tree
        self._MST = nx.minimum_spanning_tree(self.G)
        E = len(self.G.edges)
        self._complexity += int(E * np.log(E))

        self.odd_vertexes = []
        self.matching = None

        self._path = []
        self._path_sequence = {}
        self._second_path_sequence = {}
        self._nodes_sequence = {}
        self._distance = 0
        self._complexity = 0

    @property
    def MST(self):
        return self._MST

    @property
    def complexity(self):
        return self._complexity

    @complexity.setter
    def complexity(self, value):
        raise Exception("The property is read only")

    @complexity.getter
    def complexity(self):
        if self._complexity == 0:
            self.get_scenario()
        return self._complexity

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        raise Exception("The property is read only")

    @distance.getter
    def distance(self):
        if self._distance == 0:
            self.get_scenario()
        return self._distance

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        raise Exception("The property can't be set")

    @path.getter
    def path(self):
        if not self._path:
            self.get_scenario()
        return self._path

    @property
    def path_sequence(self):
        return self._path_sequence

    @path_sequence.setter
    def path_sequence(self, value):
        raise Exception("The property can't be set")

    @path_sequence.getter
    def path_sequence(self):
        if not self._path_sequence:
            self.get_scenario()
        return self._path_sequence

    @property
    def second_path_sequence(self):
        return self._second_path_sequence

    @second_path_sequence.setter
    def second_path_sequence(self, value):
        raise Exception("The property can't be set")

    @second_path_sequence.getter
    def second_path_sequence(self):
        if not self._second_path_sequence:
            self.get_scenario()
        return self._second_path_sequence

    @property
    def nodes_sequence(self):
        if not self._second_path_sequence:
            self.get_scenario()
        return self._nodes_sequence

    @nodes_sequence.setter
    def nodes_sequence(self, value):
        raise Exception("The property can't be set")

    @nodes_sequence.getter
    def nodes_sequence(self):
        if not self._path_sequence:
            self.get_scenario()
        return self._nodes_sequence

    def get_scenario(self):

        self._distance = 0

        # build a minimum spanning tree
        tmp_sequence = [[item[0], item[1]] for item in self.MST.edges]
        mst_path_sequence = {i: n for i, n in enumerate(tmp_sequence)}
        self._path_sequence = {0: []}
        self._second_path_sequence = {0: mst_path_sequence}
        self._nodes_sequence = {0: []}

        # find odd vertexes
        for node in self.MST.degree:
            if node[1] % 2 != 0:
                self.odd_vertexes.append(node[0])
                self._complexity += len(self.G.nodes)

        self.odd_vertexes = list(set(self.odd_vertexes))
        self._path_sequence.update({1: []})
        self._second_path_sequence.update({1: mst_path_sequence})
        self._nodes_sequence.update({1: self.odd_vertexes})

        # build subgraph only with odd vertices from the previous step
        self.subG = nx.Graph()
        self.subG.add_nodes_from(self.odd_vertexes)
        for node1, node2 in combinations(self.odd_vertexes, 2):
            self.subG.add_edge(node1, node2)
            self._complexity += 1

        opt_matching = optimal_matching(self.odd_vertexes, self.df_dist)
        self._complexity += len(self.odd_vertexes)**3

        self._path_sequence.update({2: {i: n for i, n in enumerate(opt_matching)}})
        self._second_path_sequence.update({2: mst_path_sequence})
        self._nodes_sequence.update({2: []})

        # adding matching edges to MST
        self._MST.add_edges_from(opt_matching)
        tmp_sequence = [[item[0], item[1]] for item in self._MST.edges]
        self._path_sequence.update({3: {i: n for i, n in enumerate(tmp_sequence)}})
        self._second_path_sequence.update({3: []})
        self._nodes_sequence.update({3: []})
        self._complexity += len(opt_matching)

        # final path
        euler_steps = []
        for edge in nx.algorithms.eulerian_path(self._MST):
            euler_steps.append(edge[1])

        self._complexity += len(list(self._MST.edges))**2

        self.logger.info(euler_steps)

        final_sequence = []
        for node in euler_steps:
            if node not in final_sequence:
                final_sequence.append(node)

        self.logger.info(final_sequence)

        final_path = [(node1, node2) for node1, node2 in zip(final_sequence[:-1], final_sequence[1:])]
        final_path.append((final_sequence[0], final_sequence[-1]))
        self._path_sequence.update({4: []})
        self._second_path_sequence.update({4: {i: n for i, n in enumerate(final_path)}})
        self._nodes_sequence.update({4: final_sequence})

        # distance calculation
        self._distance = sum([get_distance(node1, node2, df_dist=self.df_dist) for node1, node2 in final_path])

