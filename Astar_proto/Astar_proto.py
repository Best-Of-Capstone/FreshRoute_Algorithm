import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import openrouteservice
import json

cred = credentials.Certificate\
    ("gcp-credentials.json")

firebase_admin.initialize_app(cred, {
  'projectId': 'freshroute-b533b',
})

db = firestore.client()

# Reads dict from local json
with open("./data/bus.json", "r") as bus:
    map_bus = json.load(bus)
with open("./data/subway.json", "r") as subway:
    map_subway = json.load(subway)
with open("./data/subway_transfer.json", "r") as transfer:
    map_trans = json.load(transfer)


# Reads dict from Firebase
"""
map_subway = {}
map_bus = {}
map_trans = {}

# Get dictionary from Firebase
doc_sub = db.collection("SubwayTest10")
doc_sub_trans = db.collection("Transfer3")
doc_bus = db.collection("BusStop")

for tmp in doc_sub.get():
    map_subway[tmp.id] = tmp.to_dict()
    map_subway[tmp.id]['id'] = tmp.id

for tmp in doc_bus.get():
    map_bus[tmp.id] = tmp.to_dict()
    map_bus[tmp.id]['id'] = tmp.id

for tmp in doc_sub_trans.get():
    map_trans[tmp.id] = tmp.to_dict()
    map_trans[tmp.id]['id'] = tmp.id
"""


# Dump Firebase to json (Backups in case which Firebase is blocked)
"""
with open('./data/bus.json', 'w') as f:
    json.dump(map_bus, f, ensure_ascii=False, indent=4)
with open('./data/subway.json', 'w') as f:
    json.dump(map_subway, f, ensure_ascii=False, indent=4)
with open('./data/subway_transfer.json', 'w') as f:
    json.dump(map_trans, f, ensure_ascii=False, indent=4)
"""

# print(map_subway)
# print(map_bus)


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
    # octile distance
    dx = abs(node.latitude - goal.latitude)
    dy = abs(node.longitude - goal.longitude)
    return (dx + dy) + (2 ** 0.5 - 2) * min(dx, dy)


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


def a_star(map, start, end):
    start_node = set_node(start)
    end_node = set_node(end)
    """
    print(start_node.id, start_node.adj)
    print(end_node.id, end_node.adj)
    """

    open_list = []
    closed_list = []

    open_list.append(start_node)

    while open_list:

        current_node = open_list[0]
        current_idx = 0

        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_idx = index

        open_list.pop(current_idx)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                # x, y = current.position
                path.append([current.name,[current.latitude, current.longitude]])
                # path.append([current.latitude, current.longitude])
                current = current.parent
            return path[::-1]  # reverse

        children = []

        # adjacent nodes
        for new_nodes in current_node.adj:

            # update nodes
            node_position = (
                map[new_nodes['id']]['latitude'],  # X
                map[new_nodes['id']]['longitude'])  # Y

            # 동작, 관악 범위
            within_range_criteria = [
                node_position[0] > 37.516503,
                node_position[0] < 37.447182,
                node_position[1] > 126.988042,
                node_position[1] < 126.903384,
            ]

            # out of bounds when true exists
            if any(within_range_criteria):
                continue

            new_node = set_node(map[new_nodes['id']])
            children.append(new_node)

        for child in children:

            # visited nodes
            if child in closed_list:
                continue

            # updates f, g, h
            child.g = current_node.g + 1
            # child.h = ((child.position[0] - end_node.position[0]) **
            #            2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.h = heuristic(child, end_node)
            # print("position:", child.position)
            # print("from child to goal:", child.h)

            child.f = child.g + child.h

            if len([openNode for openNode in open_list
                    if child == openNode and child.g > openNode.g]) > 0:
                continue

            child.parent = current_node
            open_list.append(child)


if __name__ == "__main__":
    start_node = map_subway['2739']
    end_node = map_subway['2744']

    """
    for tmp in map_subway:
        if map_subway[tmp]['name'] == '신림':
            print(tmp)
    """

    print(a_star(map_subway, start_node, end_node))
