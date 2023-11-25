import math
import pprint
import openrouteservice
from openrouteservice.directions import directions

pp = pprint.PrettyPrinter(depth=4)
client = openrouteservice.Client(key='5b3ce3597851110001cf6248bf35ccb6f651450ea5bd337af3e428d1')

class Node:
    def __init__(self, id=None, line=None, name=None,
                 latitude=None, longitude=None, parent=None, type=None):
        self.id = id
        self.name = name
        self.line = line
        self.type = type

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
    node.type = "subway"
    for node_child in map["adj"].values():
        node.adj.append(node_child)
    return node


def set_node_bus(map):
    node = Node()
    node.id = map["id"]
    node.name = map["name"]
    node.mobile = map["ars_id"]
    node.latitude = map["latitude"]
    node.longitude = map["longitude"]
    node.type = "bus"
    for node_child in map["adj"].values():
        node.adj.append(node_child)
    return node


def combine_graph():
    # combines all subway and bus graphs :
    # discontinued due to efficiency issues
    return


def transfer_subway_bus(current_node):
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
        map_bus[tmp]['name'] = map_bus[tmp].pop('node_name')
        try:
            for tmp2 in map_bus[tmp]['adj']:
                map_bus[tmp]['adj'][tmp2]['id'] = str(map_bus[tmp]['adj'][tmp2].pop('NODE_ID'))
                map_bus[tmp]['adj'][tmp2]['latitude'] = map_bus[tmp]['adj'][tmp2].pop('Y좌표')
                map_bus[tmp]['adj'][tmp2]['longitude'] = map_bus[tmp]['adj'][tmp2].pop('X좌표')
                map_bus[tmp]['adj'][tmp2]['name'] = map_bus[tmp]['adj'][tmp2].pop('정류소명')
                map_bus[tmp]['adj'][tmp2]['line'] = map_bus[tmp]['adj'][tmp2].pop('노선명')
                map_bus[tmp]['adj'][tmp2]['ars_id'] = map_bus[tmp]['adj'][tmp2].pop('ARS_ID')
                map_bus[tmp]['adj'][tmp2]['route_id'] = str(map_bus[tmp]['adj'][tmp2].pop('ROUTE_ID'))
        except:
            print("", end='')
    return map_bus


def route_list(node1, node2):
    foo = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                     profile='foot-walking', format='geojson')
    route = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                       profile='foot-walking', format='geojson')['features'][0]['geometry']['coordinates']
    tmp = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                     profile='foot-walking', format='geojson')['features'][0]['properties']['segments']
    pp.pprint(foo)
    pp.pprint(route)
    pp.pprint(tmp)
