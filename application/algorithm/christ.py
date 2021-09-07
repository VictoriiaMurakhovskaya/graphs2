import networkx as nx
from itertools import combinations, product
import numpy as np
from networkx.algorithms.bipartite import minimum_weight_full_matching as mwfm
from .utils import distances_table, get_distance
import logging

from . import PathData

logging.basicConfig(filename='app.log', level=logging.INFO)


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
        self.G = self.create_graph(self.df, self.df_dist)

        self.subG = None

    @staticmethod
    def create_graph(df, df_dist) -> nx.Graph():
        G = nx.Graph()
        G.add_nodes_from(list(df.index))
        edge_list = []
        for index, row in df_dist.iterrows():
            edge_list.append((row.city1, row.city2, {'weight': row.dist}))
        G.add_edges_from(edge_list)
        return G

    @staticmethod
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

    @classmethod
    def path_facility(cls, df):

        cf_path = ChristAlgorithm(df)

        # minimum spanning tree
        MST = nx.minimum_spanning_tree(cf_path.G)

        # complexity definition
        E = len(cf_path.G.edges)
        complexity = int(E * np.log(E))

        # first step: build MST
        tmp_sequence = [[item[0], item[1]] for item in MST.edges]
        mst_path_sequence = {i: n for i, n in enumerate(tmp_sequence)}
        path_sequence = {0: []}
        second_path_sequence = {0: mst_path_sequence}
        nodes_sequence = {0: []}

        odd_vertexes = []
        # second step: find odd vertexes
        for node in MST.degree:
            if node[1] % 2 != 0:
                odd_vertexes.append(node[0])
                complexity += len(cf_path.G.nodes)

        odd_vertexes = list(set(odd_vertexes))
        path_sequence.update({1: []})
        second_path_sequence.update({1: mst_path_sequence})
        nodes_sequence.update({1: odd_vertexes})

        # third step: build subgraph only with odd vertices from the previous step
        subG = nx.Graph()
        subG.add_nodes_from(odd_vertexes)
        for node1, node2 in combinations(odd_vertexes, 2):
            subG.add_edge(node1, node2)
            complexity += 1

        opt_matching = cls.optimal_matching(odd_vertexes, cf_path.df_dist)
        complexity += len(odd_vertexes) ** 3

        path_sequence.update({2: {i: n for i, n in enumerate(opt_matching)}})
        second_path_sequence.update({2: mst_path_sequence})
        nodes_sequence.update({2: []})

        # forth step: adding matching edges to MST
        MST.add_edges_from(opt_matching)
        tmp_sequence = [[item[0], item[1]] for item in MST.edges]
        path_sequence.update({3: {i: n for i, n in enumerate(tmp_sequence)}})
        second_path_sequence.update({3: []})
        nodes_sequence.update({3: []})
        complexity += len(opt_matching)

        # fifth step: final path
        euler_steps = []
        for edge in nx.algorithms.eulerian_path(MST):
            euler_steps.append(edge[1])

        complexity += len(list(MST.edges)) ** 2

        cf_path.logger.info(euler_steps)

        final_sequence = []
        for node in euler_steps:
            if node not in final_sequence:
                final_sequence.append(node)

        cf_path.logger.info(final_sequence)

        final_path = [(node1, node2) for node1, node2 in zip(final_sequence[:-1], final_sequence[1:])]
        final_path.append((final_sequence[0], final_sequence[-1]))
        path_sequence.update({4: []})
        second_path_sequence.update({4: {i: n for i, n in enumerate(final_path)}})
        nodes_sequence.update({4: final_sequence})

        # distance calculation
        distance = sum([get_distance(node1, node2, df_dist=cf_path.df_dist) for node1, node2 in final_path])

        return PathData(distance=distance, complexity=complexity, path=final_path, path_sequence=path_sequence,
                        second_path_sequence=second_path_sequence, nodes_sequence=nodes_sequence)
