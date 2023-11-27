import pprint
import openrouteservice
from openrouteservice.directions import directions
from math import *

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
    return sqrt((dx ** 2) + (dy ** 2))


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


def route_list_start(node1, node2):
    foo = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                     profile='foot-walking', format='geojson')['features']
    """
    route = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                       profile='foot-walking', format='geojson')['features'][0]['geometry']['coordinates']
    tmp = directions(client, coordinates=[node1[::-1], [node2.longitude, node2.latitude]],
                     profile='foot-walking', format='geojson')['features'][0]['properties']['segments']
    """
    # pp.pprint(foo)
    return foo


def route_list_end(node1, node2):
    foo = directions(client, coordinates=[node2[::-1], [node1.longitude, node1.latitude]],
                     profile='foot-walking', format='geojson')['features']
    # pp.pprint(foo)
    return foo


def find_closest_transportation(map_bus, map_subway, coord):
    min_dist = inf
    closest_node = [[] for _ in range(2)]

    for key, point in map_bus.items():
        tmp = (coord[0] - point['latitude']) ** 2 + (coord[1] - point['longitude']) ** 2
        if tmp < min_dist and "adj" in map_bus[key]:
            min_dist = tmp
            closest_node[0] = set_node_bus(map_bus[key])
            # print(min_dist, point['latitude'], point['longitude'])
    min_dist = inf
    for key, point in map_subway.items():
        tmp2 = (coord[0] - point['latitude']) ** 2 + (coord[1] - point['longitude']) ** 2
        if tmp2 < min_dist and "adj" in map_subway[key]:
            min_dist = tmp2
            closest_node[1] = set_node_subway(map_subway[key])
            # print(min_dist, point['latitude'], point['longitude'])
    return closest_node


# Haversine function implemented without importing
# due to compatibility with numpy
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat/2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon/2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in meters. Use 3956 for miles.
    # Determines return value units.
    r = 6371
    return c * r * 1000
