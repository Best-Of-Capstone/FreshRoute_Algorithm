import math
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import openrouteservice
import json
import pprint

from Astar_subway import *
from Astar_bus import *
from Astar_combined import *

cred = credentials.Certificate\
    ("gcp-credentials.json")

firebase_admin.initialize_app(cred, {
  'projectId': 'freshroute-b533b',
})

db = firestore.client()

# print(os.getcwd())

# Reads dict from local json

with open("../data/bus.json", "r") as bus:
    map_bus = json.load(bus)
with open("../data/subway.json", "r") as subway:
    map_subway = json.load(subway)
with open("../data/subway_transfer.json", "r") as transfer:
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

# pp = pprint.PrettyPrinter(depth=4)
# pp.pprint(map_subway)
# pp.pprint(map_trans)
# print(map_bus)


def find_closest_transportation(coord):
    min_dist = math.inf
    closest_node = None

    for key, point in map_bus.items():
        tmp = (coord[0] - point['latitude']) ** 2 + (coord[1] - point['longitude']) ** 2
        if tmp < min_dist:
            min_dist = tmp
            closest_node = map_bus[key]
    for key, point in map_subway.items():
        tmp = (coord[0] - point['latitude']) ** 2 + (coord[1] - point['longitude']) ** 2
        if tmp < min_dist:
            min_dist = tmp
            closest_node = map_subway[key]
    return closest_node


def get_route_between_coordinates(start, end, target_count=1):
    start = find_closest_transportation(start)
    end = find_closest_transportation(end)
    return a_star_combined(map_subway, map_trans, map_bus, start, end)


if __name__ == "__main__":
    start = [37.49200, 126.94798]
    end = [37.50385, 126.95789]

    get_route_between_coordinates(start, end)
    # print(a_star_subway(map_subway, map_trans, start_node, end_node))
    # print(a_star_bus(map_bus, start_node, end_node))
