from tsp_solver.greedy import solve_tsp
from .utils import distances_table, get_distance
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)


class ConcordAlgorithm:
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
        self.distance_matrix = self.df_dist.pivot(index='city1', columns='city2', values='dist').fillna(0)
        self.cities_index = {i: city for i, city in enumerate(self.distance_matrix.index.tolist())}
        self.logger.info(self.cities_index)

        self._complexity = 0

        self._path = []
        self._path_sequence = []
        self._second_path_sequence = []
        self._nodes_sequence = {}
        self._distance = 0
        self._complexity = '-999'

    @property
    def complexity(self):
        return self._complexity

    @complexity.setter
    def complexity(self, value):
        raise Exception("The property is read only")

    @complexity.getter
    def complexity(self):
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
        numeric_path = solve_tsp(self.distance_matrix.values, endpoints=(0, 0))
        self._path = [self.cities_index[i] for i in numeric_path]
        self._path_sequence = {0: self._path}
        self._nodes_sequence = {0: self._path}
        self._second_path_sequence = {0: None}

        self.logger.info(numeric_path)

        final_path = [(node1, node2) for node1, node2 in zip(self._path[:-1], self._path[1:])]
        self.logger.info(final_path)

        # distance calculation
        self._distance = sum([get_distance(node1, node2, df_dist=self.df_dist) for node1, node2 in final_path])
