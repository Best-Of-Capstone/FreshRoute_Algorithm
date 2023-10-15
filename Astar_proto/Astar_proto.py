import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

cred = credentials.Certificate\
    ("gcp-credentials.json")

firebase_admin.initialize_app(cred, {
  'projectId': 'freshroute-b533b',
})

map_subway = {}

db = firestore.client()
doc_sub = db.collection("SubwayTest10")
doc_sub_trans = db.collection("Transfer3")
# doc_ref_sub = doc_sub.document("1002")
# doc_ref_st = doc_sub_trans.document("1007")

for tmp in doc_sub.get():
    map_subway[tmp.id] = tmp.to_dict()

# print(map_subway)


class Node:
    def __init__(self, id=None, line=None, name=None, lat=None, long=None, adj=None):
        self.id = id
        self.name = name
        self.line = line

        self.lat = lat
        self.long = long

        self.adj = []

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.lat == other.lat and self.long == other.long


def heuristic(node, goal):
    # octile distance
    dx = abs(node.lat - goal.lat)
    dy = abs(node.long - goal.long)
    return (dx + dy) + (2 ** 0.5 - 2) * min(dx, dy)


def aStar(maze, start, end):
    start_node = Node(start)
    end_node = Node(*end)
    print(start_node.id)
    print(end_node.id)

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
                path.append([current.lat, current.long])
                current = current.parent
            return path[::-1]  # reverse

        children = []

        # adjacent nodes
        for new_nodes in current_node.adj:

            # update nodes
            node_position = (
                current_node.lat + map_subway[new_nodes.id].latitute,  # X
                current_node.long + map_subway[new_nodes.id].longitute)  # Y

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

            new_node = Node(current_node, node_position)
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

            open_list.append(child)


if __name__ == "__main__":
    start_node = map_subway['1002']
    end_node = map_subway['2630']
    print(start_node)
    print(end_node)
    # print(aStar(map_subway, start_node, end_node))