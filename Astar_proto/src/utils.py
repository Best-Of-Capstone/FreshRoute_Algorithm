import math


class Node:
    def __init__(self, id=None, line=None, name=None,
                 latitude=None, longitude=None, parent=None):
        self.id = id
        self.name = name
        self.line = line

        self.latitude = latitude
        self.longitude = longitude

        self.parent = parent
        self.adj = []

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        """
        return self.latitude == other.latitude and self.longitude == other.longitude
        """
        if isinstance(other, Node):
            return self.id == other.id


def heuristic(node, goal):
    dx = abs(node.latitude - goal.latitude)
    dy = abs(node.longitude - goal.longitude)
    # octile distance
    # return (dx + dy) + (2 ** 0.5 - 2) * min(dx, dy)
    return math.sqrt((dx ** 2) + (dy ** 2))


def set_node(map):
    node = Node()
    node.id = map["id"]
    node.line = map["line"]
    node.name = map["name"]
    node.latitude = map["latitude"]
    node.longitude = map["longitude"]
    for node_child in map["adj"].values():
        node.adj.append(node_child)
    return node

def combine_graph():
    return