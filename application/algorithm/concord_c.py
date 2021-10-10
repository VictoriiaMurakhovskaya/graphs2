from concorde.tsp import TSPSolver
from .utils import distances_table, get_distance
import logging

from . import PathData

logging.basicConfig(filename='app.log', level=logging.INFO)


class ConcordCImplemented:
    """
    Concord algorithm implemented with C++
    Index = cities
    Columns = longitude, latitude
    """

    def __init__(self, df):
        self.logger = logging.getLogger('main_flow')
        self.logger.setLevel('INFO')

        self.df = df
        self.df_dist = distances_table(df)

    @staticmethod
    def path_facility(df):
        cc_path = ConcordCImplemented(df)

        distance_matrix = cc_path.df_dist.pivot(index='city1', columns='city2', values='dist').fillna(0)
        cities_index = {i: city for i, city in enumerate(distance_matrix.index.tolist())}

        solver = TSPSolver.from_data(
                                            df.lat,
                                            df.long,
                                            norm="GEO"
                                            )
        numeric_path = solver.solve()
        tour = numeric_path.tour
        path = [cities_index[i] for i in tour]
        path.append(path[0])
        path_sequence = {0: path}
        nodes_sequence = {0: path}
        second_path_sequence = {0: None}

        final_path = [(node1, node2) for node1, node2 in zip(path[:-1], path[1:])]

        # distance calculation
        distance = sum([get_distance(node1, node2, df_dist=cc_path.df_dist) for node1, node2 in final_path])

        return PathData(distance=distance, complexity=0, path=final_path, path_sequence=path_sequence,
                        second_path_sequence=second_path_sequence, nodes_sequence=nodes_sequence)


