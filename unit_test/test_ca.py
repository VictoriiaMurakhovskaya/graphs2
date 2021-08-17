from unittest import TestCase
import unittest
from pathlib import Path
import pandas as pd
from application.algorithm import get_distance
from application.algorithm import optimal_matching as om
from application.algorithm import distances_table

from application.algorithm import ChristAlgorithm
import numpy as np


class TestApp(TestCase):

    def setUp(self) -> None:
        ROOT_PATH = str(Path(__file__).parent.parent)
        DATA_PATH = ROOT_PATH + '/assets/gps_cities.xlsx'
        self.df = pd.read_excel(DATA_PATH, index_col=0)
        try:
            self.ca = ChristAlgorithm(self.df)
        except Exception as e:
            print(e)
            self.ca = None
        self.df_dist = distances_table(self.df)

    def test_object_creation(self):
        self.assertIsNotNone(self.ca)

    def test_MST(self):
        self.assertIsNotNone(self.ca.MST)

    def test_distance(self):
        df = self.ca.df
        df_dist = self.ca.df_dist
        node1 = df.index[0]
        node2 = df.index[1]
        dist = get_distance(node1, node2, df_dist)
        self.assertGreater(dist, 0)

    def test_optimal_matching(self):
        nodes = list(self.df.index)[:6]
        mwfm = om(nodes, self.ca.df_dist)

    def test_get_scenario(self):
        self.ca.get_scenario()

    @unittest.skip('Too long test')
    def test_distance_with_external(self):
        cities = list(self.df.index)
        adj = np.zeros((len(cities), len(cities)))
        for i, city1 in enumerate(cities):
            for j, city2 in enumerate(cities):
                if city1 == city2:
                    adj[i, j] = 0
                else:
                    adj[i, j] = get_distance(city1, city2, self.df_dist)

        lst = list(range(len(cities)))

        from itertools import permutations
        min_distance = 100000
        for combo in permutations(lst, len(lst)):
            if (dist := np.sum([adj[combo[i - 1], combo[i]] for i in range(len(combo))])) < min_distance:
                min_distance = dist
        print(min_distance)










