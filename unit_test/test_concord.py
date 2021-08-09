from tsp_solver.greedy import solve_tsp
from unittest import TestCase
from pathlib import Path
import pandas as pd
from algorithm.christ import distances_table


class TestConcord(TestCase):
    def setUp(self) -> None:
        ROOT_PATH = str(Path(__file__).parent.parent)
        DATA_PATH = ROOT_PATH + '/assets/gps_cities.xlsx'
        self.df = pd.read_excel(DATA_PATH, index_col=0)
        distance_table = distances_table(self.df, permute=True)
        self.distance_matrix = distance_table.pivot(index='city1', columns='city2', values='dist').fillna(0)

    def test_rsp(self):
        path = solve_tsp(self.distance_matrix.values, endpoints=(0, 0))
        print('!')