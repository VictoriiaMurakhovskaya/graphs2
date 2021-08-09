import pandas as pd
from itertools import combinations
from geopy.distance import geodesic
import numpy as np
from .utils import distances_table


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
        :param start: the start point (is significant for the Nearest neighbour
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
    def nodes_sequence(self):
        if not self._path_sequence:
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
                df_loc = self.distances.loc[(self.distances['city1'] == city2) & (self.distances['city2'] == city1)].copy()
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

    def get_scenario(self):
        """
        Updates all the properties basing on current df
        :return:
        """
        self._distance = 0
        self._path = self.find_path()
        self._path_sequence = {i: self._path[:i + 2] for i in range(len(self._path) - 1)}

        self._nodes_sequence = {i: self._path[: i + 2] for i in range(len(self._path) - 2)}
        self._nodes_sequence.update({len(self._nodes_sequence.keys()):
                                         self._nodes_sequence[len(self._nodes_sequence.keys()) - 1]})

        self._distance = np.sum([self.get_distance(self._path[i],
                                                   self._path[i + 1]) for i in range(len(self._path) - 1)])
