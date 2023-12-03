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


def get_route_between_coord(start, end, cong, mode, target_count=1):
    route = {"RESULT_CODE": 200, "RESULT_MSG": "OK", "RESULT_DATA": {"routeList": []}}
    tmp = [0 if mode < 2 else 1, 0 if mode == 1 else 1]
    start_near = find_closest_transportation(map_bus, map_subway, start, target_count)[tmp[0]]
    end_near = find_closest_transportation(map_bus, map_subway, end, target_count)[tmp[1]]
    # print(start.name, end.name)
    # print([start, [start_near.latitude, start_near.longitude]])
    return route_to_format(route, target_count, start, start_near, end, end_near)


def route_to_format(result, target_count, start, start_near, end, end_near):
    # start_route = route_list_start(start, start_near)
    public_route_tot = a_star_combined(map_subway, map_trans, map_bus, start_near, end_near, target_count)
    # end_route = route_list_end(end_near, end)

    for i in range(target_count):
        public_route = public_route_tot[i]
        start_transport, end_transport = public_route[0][1], public_route[-1][1]
        # start
        """
        for j, route in enumerate(start_route):
            # print(route)
            route_dict = {
                "id": i,
                "description": f"Route {i}",
                "route": {
                    "distance": route["properties"]["summary"]["distance"],
                    "duration": route["properties"]["summary"]["duration"],
                    "startTransport": start_transport,
                    "endTransport": end_transport,
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
        """
        route_dict = {
            "id": i,
            "description": f"Route {i}",
            "route": {
                "distance": 0,
                "duration": 0,
                "startTransport": start_transport,
                "endTransport": end_transport,
                "steps": [],
                "coordinates": []
            }
        }
        result["RESULT_DATA"]["routeList"].append(route_dict)

        # public transportation route

        # tmp_long, tmp_lat = result["RESULT_DATA"]["routeList"][0]["route"]["coordinates"][-1]
        # tmp_dist = round(haversine(tmp_long, tmp_lat, public_route[0][1][1], public_route[0][1][0]), 1)
        # tmp_duration = round(tmp_dist / 833 * 60, 1) \
        #     if public_route[0][2] == "subway" else round(tmp_dist / 333 * 60, 1)
        tmp_dist, tmp_duration = 0, 0
        tmp_type, tmp_description = 0, 0
        if public_route[0][2] == "subway":
            tmp_type = public_route[0][0] + "역에서 " + public_route[0][3] + " 탑승"
            tmp_description = public_route[0][0] + " (" + public_route[0][3] + ")"
        elif public_route[0][2] == "bus":
            tmp_type = "버스 탑승"
            tmp_description = public_route[0][0]

        # tmp_waypoints = result["RESULT_DATA"]["routeList"][0]["route"]["steps"][-1]["wayPoints"][1]
        tmp_waypoints = 0
        tmp_step_dict = {
            "distance": tmp_dist,
            "duration": tmp_duration,
            "type": tmp_type,
            "name": tmp_description,
            "wayPoints": [tmp_waypoints, tmp_waypoints + 1]
        }
        result["RESULT_DATA"]["routeList"][i]["route"]["distance"] += tmp_dist
        result["RESULT_DATA"]["routeList"][i]["route"]["duration"] += tmp_duration
        result["RESULT_DATA"]["routeList"][i]["route"]["steps"].append(tmp_step_dict)
        result["RESULT_DATA"]["routeList"][i]["route"]["coordinates"].append(
            [public_route[0][1][1], public_route[0][1][0]])
        tmp_waypoints += 1
        for j in range(1, len(public_route)):
            tmp_long, tmp_lat = result["RESULT_DATA"]["routeList"][i]["route"]["coordinates"][-1]
            tmp_dist = round(haversine(tmp_long, tmp_lat, public_route[j][1][1], public_route[j][1][0]), 1)
            tmp_duration = round(tmp_dist / 833 * 60, 1) \
                if public_route[j][2] == "subway" else round(tmp_dist / 333 * 60, 1)
            if public_route[j][2] == "subway":
                tmp_type = public_route[j][0] + "역에서 " + public_route[j][3] + (
                    " 환승" if public_route[j - 1][0] == public_route[j][0] else (
                        " 탑승" if j != len(public_route) - 1 else " 하차"))
                tmp_description = public_route[j][0] + " (" + public_route[j][3] + ")"
            elif public_route[j][2] == "bus":
                tmp_type = "버스 탑승"
                tmp_description = public_route[j][0]

            tmp_step_dict = {
                "distance": tmp_dist,
                "duration": tmp_duration,
                "type": tmp_type,
                "name": tmp_description,
                "wayPoints": [tmp_waypoints, tmp_waypoints + 1]
            }
            result["RESULT_DATA"]["routeList"][i]["route"]["distance"] += tmp_dist
            result["RESULT_DATA"]["routeList"][i]["route"]["duration"] += tmp_duration
            result["RESULT_DATA"]["routeList"][i]["route"]["steps"].append(tmp_step_dict)
            result["RESULT_DATA"]["routeList"][i]["route"]["coordinates"].append(
                [public_route[j][1][1], public_route[j][1][0]])
            tmp_waypoints += 1

        # end
        """
        for j, route in enumerate(end_route):
            result["RESULT_DATA"]["routeList"][i]["route"]["distance"] \
                += route["properties"]["summary"]["distance"]
            result["RESULT_DATA"]["routeList"][i]["route"]["duration"] \
                += route["properties"]["summary"]["duration"]
            for tmp in route["geometry"]["coordinates"]:
                result["RESULT_DATA"]["routeList"][i]["route"]["coordinates"].append(tmp)
            for step in route["properties"]["segments"][0]["steps"]:
                step_dict = {
                    "distance": step["distance"],
                    "duration": step["duration"],
                    "type": step["type"],
                    "name": step["instruction"],
                    "wayPoints": [step["way_points"][0] + tmp_waypoints, step["way_points"][1] + tmp_waypoints]
                }
                result["RESULT_DATA"]["routeList"][i]["route"]["steps"].append(step_dict)
            tmp_waypoints += 1
        # result["RESULT_DATA"]["routeList"].append(route_dict)
        """
        result["RESULT_DATA"]["routeList"][i]["route"]["distance"] \
            = round(result["RESULT_DATA"]["routeList"][i]["route"]["distance"], 1)
        result["RESULT_DATA"]["routeList"][i]["route"]["duration"] \
            = round(result["RESULT_DATA"]["routeList"][i]["route"]["duration"], 1)

    return result


if __name__ == "__main__":
    # time_start = time.time()
    """
    start = [37.48912, 126.94616]
    end = [37.50495, 126.95390]
    """
    """
    start = [37.49602, 126.953822]
    end = [37.48236, 126.94189]
    """
    start = [37.48912, 126.94616]
    end = [37.50495, 126.95390]
    cong = 0
    mode = 0
    tar = 2
    route_list = get_route_between_coord(start, end, cong, mode, tar)
    pp.pprint(route_list)
    # print(a_star_subway(map_subway, map_trans, start_node, end_node))
    # print(a_star_bus(map_bus, start_node, end_node))

    # print(time.time() - time_start)

    with open('route_list.json', 'w', encoding='utf8') as f:
        json.dump(route_list, f, indent=4, ensure_ascii=False)
    """
    foo = {"data":{"RESULT_CODE":200,"RESULT_DATA":{"routeList":[{"description":"Route 0","id":0,"route":{"coordinates":[[126.941892,37.482362],[126.952739,37.481247],[126.963693,37.47693],[126.981544,37.476538],[126.981651,37.476955],[126.981989,37.486263],[126.981605,37.485196],[126.971251,37.484596],[126.953822,37.496029],[126.94791,37.502834]],"distance":8656.5,"duration":623.5,"endTransport":[37.502834,126.94791],"startTransport":[37.482362,126.941892],"steps":[{"distance":0,"duration":0,"name":"\ubd09\ucc9c (2\ud638\uc120)","type":"\ubd09\ucc9c\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[0,1]},{"distance":965.1,"duration":69.5,"name":"\uc11c\uc6b8\ub300\uc785\uad6c (2\ud638\uc120)","type":"\uc11c\uc6b8\ub300\uc785\uad6c\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[1,2]},{"distance":1079.2,"duration":77.7,"name":"\ub099\uc131\ub300 (2\ud638\uc120)","type":"\ub099\uc131\ub300\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[2,3]},{"distance":1575.9,"duration":113.5,"name":"\uc0ac\ub2f9 (2\ud638\uc120)","type":"\uc0ac\ub2f9\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[3,4]},{"distance":47.3,"duration":3.4,"name":"\uc0ac\ub2f9 (4\ud638\uc120)","type":"\uc0ac\ub2f9\uc5ed\uc5d0\uc11c 4\ud638\uc120 \ud658\uc2b9","wayPoints":[4,5]},{"distance":1035.4,"duration":74.6,"name":"\uc774\uc218 (4\ud638\uc120)","type":"\uc774\uc218\uc5ed\uc5d0\uc11c 4\ud638\uc120 \ud0d1\uc2b9","wayPoints":[5,6]},{"distance":123.4,"duration":8.9,"name":"\uc774\uc218 (7\ud638\uc120)","type":"\uc774\uc218\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud658\uc2b9","wayPoints":[6,7]},{"distance":916.0,"duration":66.0,"name":"\ub0a8\uc131 (7\ud638\uc120)","type":"\ub0a8\uc131\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud0d1\uc2b9","wayPoints":[7,8]},{"distance":1995.2,"duration":143.7,"name":"\uc22d\uc2e4\ub300\uc785\uad6c (7\ud638\uc120)","type":"\uc22d\uc2e4\ub300\uc785\uad6c\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud0d1\uc2b9","wayPoints":[8,9]},{"distance":919.0,"duration":66.2,"name":"\uc0c1\ub3c4 (7\ud638\uc120)","type":"\uc0c1\ub3c4\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud558\ucc28","wayPoints":[9,10]}]}}]},"RESULT_MSG":"OK"},"status_number":200}
    with open('foo.json', 'w', encoding='utf8') as f:
        json.dump(foo, f, indent=4, ensure_ascii=False)
    """
