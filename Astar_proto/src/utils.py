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


def set_node_subway(map):
    node = Node()
    node.id = map["id"]
    node.line = map["line"]
    node.name = map["name"]
    node.latitude = map["latitude"]
    node.longitude = map["longitude"]
    for node_child in map["adj"].values():
        node.adj.append(node_child)
    return node


def set_node_bus(map):
    node = Node()
    node.id = map["id"]
    node.name = map["node_name"]
    node.mobile = map["ars_id"]
    node.latitude = map["latitude"]
    node.longitude = map["longitude"]
    for node_child in map["adj"].values():
        node.adj.append(node_child)
    return node

def combine_graph():

    return


def convert_bus(map_bus):
    # Redundant values
    #
    # ARS_ID, mobile_number ()
    # ID, NODE_ID 동일 ()
    # ROUTE_ID, 노선명 1대1 대응

    # pp.pprint(map_bus)

    for tmp in map_bus:
        map_bus[tmp]['id'] = map_bus[tmp].pop('id')
        map_bus[tmp]['ars_id'] = map_bus[tmp].pop('mobile_number')
        try:
            for tmp2 in map_bus[tmp]['adj']:
                map_bus[tmp]['adj'][tmp2]['id'] = str(map_bus[tmp]['adj'][tmp2].pop('NODE_ID'))
                map_bus[tmp]['adj'][tmp2]['latitude'] = map_bus[tmp]['adj'][tmp2].pop('Y좌표')
                map_bus[tmp]['adj'][tmp2]['longitude'] = map_bus[tmp]['adj'][tmp2].pop('X좌표')
                map_bus[tmp]['adj'][tmp2]['node_name'] = map_bus[tmp]['adj'][tmp2].pop('정류소명')
                map_bus[tmp]['adj'][tmp2]['line'] = map_bus[tmp]['adj'][tmp2].pop('노선명')
                map_bus[tmp]['adj'][tmp2]['ars_id'] = map_bus[tmp]['adj'][tmp2].pop('ARS_ID')
                map_bus[tmp]['adj'][tmp2]['route_id'] = str(map_bus[tmp]['adj'][tmp2].pop('ROUTE_ID'))
        except:
            print("", end='')
    return map_bus