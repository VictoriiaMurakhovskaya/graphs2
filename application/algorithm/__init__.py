from .algorithm import NearestNeighbour
from .christ import ChristAlgorithm
from .concord import ConcordAlgorithm

from pandas import DataFrame

from dataclasses import dataclass, field


@dataclass
class PathData:
    distance: float = 0
    complexity: int = 0

    path: list = field(default_factory=list)
    path_sequence: dict = field(default_factory=dict)
    second_path_sequence: list = field(default_factory=list)
    nodes_sequence: dict = field(default_factory=dict)


class PathMaker:

    @staticmethod
    def return_path_data(alg: str, work_df: DataFrame):
        if alg == 'NN':
            path_info = NearestNeighbour(work_df, work_df.index[0])
        elif alg == 'CA':
            path_info = ChristAlgorithm(work_df)
        elif alg == 'CC':
            path_info = ConcordAlgorithm(work_df)
        else:
            raise ValueError("Incorrect algorithm type")

        path_data = PathData()

        path_data.distance = path_info.distance
        path_data.complexity = path_info.complexity

        path_data.path = path_info.path
        path_data.path_sequence = path_info.path_sequence
        if alg != 'NN':
            path_data.second_path_sequence = path_info.second_path_sequence
        else:
            path_data.second_path_sequence = {k: [] for k, v in path_data.path_sequence.items()}
        path_data.nodes_sequence = path_info.nodes_sequence

        return path_data
