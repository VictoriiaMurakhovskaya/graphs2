from dataclasses import dataclass, field


@dataclass
class PathData:
    distance: float = 0
    complexity: int = 0

    path: list = field(default_factory=list)
    path_sequence: dict = field(default_factory=dict)
    second_path_sequence: dict = field(default_factory=dict)
    nodes_sequence: dict = field(default_factory=dict)


