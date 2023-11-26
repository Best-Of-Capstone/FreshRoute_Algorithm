import math
import os
import sys
import time
import firebase_admin
import json


from firebase_admin import credentials
from firebase_admin import firestore

from Astar_subway import *
from Astar_bus import *
from Astar_combined import *
from utils import *

sys.setrecursionlimit(2000)

"""
cred = credentials.Certificate\
    ("gcp-credentials.json")

firebase_admin.initialize_app(cred, {
  'projectId': 'freshroute-b533b',
})

db = firestore.client()
"""

# print(os.getcwd())

# Reads dict from local json

with open("../data/bus.json", "r") as bus:
    map_bus = convert_bus(json.load(bus))
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

pp = pprint.PrettyPrinter(depth=4)
# pp.pprint(map_subway)
# pp.pprint(map_trans)
# print(map_bus)


def get_route_between_coord(start, end, target_count=1):
    route = {"RESULT_CODE": 200, "RESULT_MSG": "OK", "RESULT_DATA": {"routeList": []}}
    start_near = find_closest_transportation(map_bus, map_subway, start)[1]
    end_near = find_closest_transportation(map_bus, map_subway, end)[1]
    # print(start.name, end.name)
    # print([start, [start_near.latitude, start_near.longitude]])
    return route_to_format(route, target_count, start, start_near, end, end_near)


def route_to_format(result, target_count, start, start_near, end, end_near):
    start_route = route_list_start(start, start_near)
    public_route = a_star_combined(map_subway, map_trans, map_bus, start_near, end_near)
    end_route = route_list_end(end_near, end)

    for i in range(target_count):
        # start
        for j, route in enumerate(start_route):
            # print(route)
            route_dict = {
                "id": i,
                "description": f"Route {i}",
                "route": {
                    "distance": route["properties"]["summary"]["distance"],
                    "duration": route["properties"]["summary"]["duration"],
                    "steps": [],
                    "coordinates": route["geometry"]["coordinates"]
                }
            }
            for step in route["properties"]["segments"][0]["steps"]:
                step_dict = {
                    "distance": step["distance"],
                    "duration": step["duration"],
                    "type": step["type"],
                    "name": step["instruction"],
                    "wayPoints": step["way_points"]
                }
                route_dict["route"]["steps"].append(step_dict)
            result["RESULT_DATA"]["routeList"].append(route_dict)
        # public transportation route

        # end
        for j, route in enumerate(end_route):
            route_dict = {
                "id": i,
                "description": f"Route {i}",
                "route": {
                    "distance": route["properties"]["summary"]["distance"],
                    "duration": route["properties"]["summary"]["duration"],
                    "steps": [],
                    "coordinates": route["geometry"]["coordinates"]
                }
            }
            for step in route["properties"]["segments"][0]["steps"]:
                step_dict = {
                    "distance": step["distance"],
                    "duration": step["duration"],
                    "type": step["type"],
                    "name": step["instruction"],
                    "wayPoints": step["way_points"]
                }
                route_dict["route"]["steps"].append(step_dict)
            result["RESULT_DATA"]["routeList"].append(route_dict)

    return result


if __name__ == "__main__":
    # time_start = time.time()
    """
    start = [37.48918, 126.94612]
    end = [37.50501, 126.95398]
    """
    """
    start = [37.49602, 126.953822]
    end = [37.48236, 126.94189]
    """
    start = [37.49602, 126.953822]
    end = [37.48236, 126.94189]
    route_list = get_route_between_coord(start, end)
    pp.pprint(route_list)
    # print(a_star_subway(map_subway, map_trans, start_node, end_node))
    # print(a_star_bus(map_bus, start_node, end_node))

    # print(time.time() - time_start)

    with open('route_list.json', 'w') as f:
        json.dump(route_list, f, indent=4)
