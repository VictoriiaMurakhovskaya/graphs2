import pandas as pd
import numpy as np
from .utils import distances_table
from . import PathData


class NearestNeighbour:
    """
    Nearest neighbour algorithm implementation for Tradesman problem
    Returns necessary data via properties
    """

    def __init__(self, nodes, start):
        """
        Class constructor
        :param nodes: the list of nodes as DataFrame:
            index - city name
            columns - lat, long
        :param start: the start point (is significant for the Nearest neighbour)
        """
        self.df = nodes
        self.start = start
        self._path = []
        self._path_sequence = []
        self._nodes_sequence = {}
        self._distance = 0
        self._complexity = 0

        self.df = self.df.sort_values(by='city', ascending=True)
        self.df['city'] = self.df.index
        self.distances = self.get_distances()

    def neighbour(self, current, visited):
        """
        Defines the nearest neighbour
        :param current: the node for which the neighbour should be defined
        :param visited: already visited nodes (excluded from the search list)
        :return:
        """
        df1 = self.distances.loc[(self.distances['city1'] == current) & (
            self.distances['city2'].isin([item for item in self.df.index if item not in visited]))].copy()
        df2 = self.distances.loc[(self.distances['city2'] == current) & (
            self.distances['city1'].isin([item for item in self.df.index if item not in visited]))].copy()
        res = pd.Series(data=list(df1.dist) + list(df2.dist), index=list(df1['city2']) + list(df2['city1']))
        self._complexity += len(res)
        return res.idxmin()

    def get_distances(self):
        """
        Defines distances for all the cities combinations using geopy
        :return: the DataFrame with distances
        """
        cities = self.df.copy()
        return distances_table(cities)

    def get_distance(self, city1, city2):
        """
        Defines distance between the city1 and city2 using geopy
        :param city1: city 1
        :param city2: city 2
        :return:
        """
        if len(self.distances) > 0:
            df_loc = self.distances.loc[(self.distances['city1'] == city1) & (self.distances['city2'] == city2)].copy()
            if len(df_loc) == 0:
                df_loc = self.distances.loc[
                    (self.distances['city1'] == city2) & (self.distances['city2'] == city1)].copy()
            return df_loc.at[df_loc.index[0], 'dist']
        else:
            return 0

    def find_path(self):
        """
        The main method which looks for the path
        :return:
        """
        sequence = []
        current = self.start
        while len([self.start] + sequence) < len(self.df):
            current = self.neighbour(current, [self.start] + sequence)
            sequence.append(current)

        return [self.start] + sequence + [self.start]

    @staticmethod
    def path_facility(nodes, start) -> PathData:
        """
        Path facility using nearest neighbour algorithm
        :return: path data
        """
        nn_path = NearestNeighbour(nodes, start)

        path = nn_path.find_path()

        path_sequence = {i: path[:i + 2] for i in range(len(path) - 1)}
        second_path_sequence = {k: [] for k, v in path_sequence.items()}

        nodes_sequence = {i: path[: i + 2] for i in range(len(path) - 2)}
        nodes_sequence.update({len(nodes_sequence.keys()):
                                   nodes_sequence[len(nodes_sequence.keys()) - 1]})

        distance = float(np.sum([nn_path.get_distance(path[i], path[i + 1]) for i in range(len(path) - 1)]))

        return PathData(distance=distance, complexity=nn_path._complexity, path=path, path_sequence=path_sequence,
                        second_path_sequence=second_path_sequence, nodes_sequence=nodes_sequence)
