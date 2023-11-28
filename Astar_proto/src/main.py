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
    # print(public_route)

    start_transport, end_transport = public_route[0][1], public_route[-1][1]

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
        # public transportation route

        tmp_long, tmp_lat = result["RESULT_DATA"]["routeList"][0]["route"]["coordinates"][-1]
        tmp_dist = round(haversine(tmp_long, tmp_lat, public_route[0][1][1], public_route[0][1][0]), 1)
        tmp_duration = round(tmp_dist / 833 * 60, 1) \
            if public_route[0][2] == "subway" else round(tmp_dist / 333 * 60, 1)
        tmp_type, tmp_description = 0, 0
        if public_route[0][2] == "subway":
            tmp_type = public_route[0][0] + "역에서 " + public_route[0][3] + " 탑승"
            tmp_description = public_route[0][0] + " (" + public_route[0][3] + ")"
        elif public_route[0][2] == "bus":
            tmp_type = "버스 탑승"
            tmp_description = public_route[0][0]

        tmp_waypoints = result["RESULT_DATA"]["routeList"][0]["route"]["steps"][-1]["wayPoints"][1]
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
                print(j, len(public_route) - 1)
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

        result["RESULT_DATA"]["routeList"][i]["route"]["distance"] \
            = round(result["RESULT_DATA"]["routeList"][i]["route"]["distance"], 1)
        result["RESULT_DATA"]["routeList"][i]["route"]["duration"] \
            = round(result["RESULT_DATA"]["routeList"][i]["route"]["duration"], 1)

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
    start = [37.48918, 126.94612]
    end = [37.50501, 126.95398]
    route_list = get_route_between_coord(start, end)
    pp.pprint(route_list)
    # print(a_star_subway(map_subway, map_trans, start_node, end_node))
    # print(a_star_bus(map_bus, start_node, end_node))

    # print(time.time() - time_start)

    with open('route_list.json', 'w', encoding='utf8') as f:
        json.dump(route_list, f, indent=4, ensure_ascii=False)


    foo = {"data":{"RESULT_CODE":200,"RESULT_DATA":{"routeList":[{"description":"Route 0","id":0,"route":{"coordinates":[[126.946126,37.489181],[126.946348,37.488602],[126.946521,37.48787],[126.946903,37.487883],[126.946994,37.487738],[126.947232,37.4875],[126.947287,37.487446],[126.94738,37.487271],[126.94739,37.487093],[126.947341,37.486905],[126.947011,37.486949],[126.946261,37.486994],[126.946253,37.486908],[126.946277,37.486773],[126.946438,37.486088],[126.946363,37.486051],[126.946329,37.486006],[126.946307,37.485905],[126.946381,37.485444],[126.946442,37.485343],[126.946656,37.485067],[126.946703,37.485041],[126.946821,37.485033],[126.946786,37.484775],[126.946171,37.48482],[126.946137,37.484525],[126.946095,37.484529],[126.945747,37.484413],[126.945677,37.48439],[126.945284,37.484257],[126.945249,37.484258],[126.944923,37.484267],[126.944595,37.484267],[126.944396,37.484267],[126.944262,37.484267],[126.943806,37.484256],[126.94379,37.484085],[126.943772,37.483931],[126.943746,37.483729],[126.943683,37.483255],[126.943096,37.48331],[126.94234,37.483395],[126.94233,37.483372],[126.942265,37.483267],[126.942226,37.483128],[126.942243,37.483081],[126.942215,37.483001],[126.942213,37.482913],[126.942045,37.482438],[126.9417,37.482515],[126.941644,37.482362],[126.941876,37.482313],[126.941892,37.482362],[126.952739,37.481247],[126.963693,37.47693],[126.981544,37.476538],[126.981651,37.476955],[126.981989,37.486263],[126.981605,37.485196],[126.971251,37.484596],[126.953822,37.496029],[126.94791,37.502834],[126.953972,37.504999],[126.953942,37.505013],[126.954139,37.505159],[126.954205,37.505103],[126.954248,37.505135],[126.954589,37.504995],[126.954784,37.505182],[126.955466,37.504925],[126.955558,37.504986],[126.955997,37.504812],[126.95602,37.504732],[126.956468,37.504552],[126.95666,37.504514],[126.956749,37.50453],[126.957184,37.504454],[126.957278,37.504408],[126.95762,37.50436],[126.957617,37.503952],[126.957383,37.503794],[126.957386,37.503369],[126.957389,37.503001],[126.95729,37.502947],[126.956147,37.502958],[126.955646,37.503243],[126.955644,37.503722],[126.955505,37.503896],[126.955332,37.503961],[126.954847,37.503988],[126.954126,37.504274],[126.954072,37.504345],[126.954067,37.504419],[126.954167,37.504744],[126.954196,37.504852],[126.953731,37.505017],[126.953606,37.505002],[126.953606,37.504814],[126.953448,37.504815],[126.953272,37.504779],[126.953327,37.504374],[126.952891,37.504355],[126.952704,37.504326],[126.952667,37.504259],[126.95278,37.503745],[126.952788,37.503662],[126.952452,37.50364],[126.95212,37.503814],[126.951751,37.503816],[126.951795,37.503655],[126.951853,37.503281],[126.951589,37.503215],[126.951546,37.503189],[126.951404,37.50303],[126.95131,37.502962],[126.950886,37.502749],[126.950228,37.502506],[126.949964,37.502525],[126.949916,37.5025],[126.949548,37.502303],[126.949357,37.502203],[126.949296,37.502171],[126.948766,37.502734],[126.948285,37.502474],[126.948185,37.502593],[126.94796,37.50286]],"distance":11917.1,"duration":2967.4,"endTransport":[37.502834,126.94791],"startTransport":[37.482362,126.941892],"steps":[{"distance":150.1,"duration":108.1,"name":"Head south on \uc591\ub155\ub85c","type":11,"wayPoints":[0,2]},{"distance":33.7,"duration":24.3,"name":"Turn left onto \uc591\ub155\ub85c","type":0,"wayPoints":[2,3]},{"distance":121.8,"duration":87.7,"name":"Turn right onto \uc740\ucc9c\ub85c19\uae38","type":1,"wayPoints":[3,9]},{"distance":95.8,"duration":69.0,"name":"Turn right onto \uc740\ucc9c\ub85c","type":1,"wayPoints":[9,11]},{"distance":102.2,"duration":73.6,"name":"Turn left onto \uc591\ub155\ub85c7\uae38","type":0,"wayPoints":[11,14]},{"distance":140.7,"duration":101.3,"name":"Turn right onto \uc591\ub155\ub85c7\uae38","type":1,"wayPoints":[14,22]},{"distance":28.9,"duration":20.8,"name":"Turn right onto \uc591\ub155\ub85c","type":1,"wayPoints":[22,23]},{"distance":54.5,"duration":39.3,"name":"Turn right onto \uc591\ub155\ub85c5\uae38","type":1,"wayPoints":[23,24]},{"distance":32.9,"duration":23.7,"name":"Turn left onto \uc591\ub155\ub85c1\uac00\uae38","type":0,"wayPoints":[24,25]},{"distance":211.9,"duration":152.5,"name":"Turn right onto \ubd09\ucc9c\ub85c33\uac00\uae38","type":1,"wayPoints":[25,35]},{"distance":111.8,"duration":80.5,"name":"Turn left onto \ubd09\ucc9c\ub85c33\uae38","type":0,"wayPoints":[35,39]},{"distance":119.5,"duration":86.0,"name":"Turn right onto \ubd09\ucc9c\ub85c","type":1,"wayPoints":[39,41]},{"distance":15.7,"duration":11.3,"name":"Turn left onto \ubd09\ucc9c\ub85c","type":0,"wayPoints":[41,43]},{"distance":95.2,"duration":68.5,"name":"Turn slight left onto \ub0a8\ubd80\uc21c\ud658\ub85c","type":4,"wayPoints":[43,48]},{"distance":31.6,"duration":22.7,"name":"Turn right onto \ub0a8\ubd80\uc21c\ud658\ub85c, 92","type":1,"wayPoints":[48,49]},{"distance":17.7,"duration":12.7,"name":"Turn left","type":0,"wayPoints":[49,50]},{"distance":21.1,"duration":15.2,"name":"Turn left onto \ub0a8\ubd80\uc21c\ud658\ub85c, 92","type":0,"wayPoints":[50,51]},{"distance":0.0,"duration":0.0,"name":"Arrive at \ub0a8\ubd80\uc21c\ud658\ub85c, 92, on the left","type":10,"wayPoints":[51,51]},{"distance":5.6,"duration":0.4,"name":"\ubd09\ucc9c (2\ud638\uc120)","type":"\ubd09\ucc9c\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[51,52]},{"distance":965.1,"duration":69.5,"name":"\uc11c\uc6b8\ub300\uc785\uad6c (2\ud638\uc120)","type":"\uc11c\uc6b8\ub300\uc785\uad6c\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[52,53]},{"distance":1079.2,"duration":77.7,"name":"\ub099\uc131\ub300 (2\ud638\uc120)","type":"\ub099\uc131\ub300\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[53,54]},{"distance":1575.9,"duration":113.5,"name":"\uc0ac\ub2f9 (2\ud638\uc120)","type":"\uc0ac\ub2f9\uc5ed\uc5d0\uc11c 2\ud638\uc120 \ud0d1\uc2b9","wayPoints":[54,55]},{"distance":47.3,"duration":3.4,"name":"\uc0ac\ub2f9 (4\ud638\uc120)","type":"\uc0ac\ub2f9\uc5ed\uc5d0\uc11c 4\ud638\uc120 \ud658\uc2b9","wayPoints":[55,56]},{"distance":1035.4,"duration":74.6,"name":"\uc774\uc218 (4\ud638\uc120)","type":"\uc774\uc218\uc5ed\uc5d0\uc11c 4\ud638\uc120 \ud0d1\uc2b9","wayPoints":[56,57]},{"distance":123.4,"duration":8.9,"name":"\uc774\uc218 (7\ud638\uc120)","type":"\uc774\uc218\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud658\uc2b9","wayPoints":[57,58]},{"distance":916.0,"duration":66.0,"name":"\ub0a8\uc131 (7\ud638\uc120)","type":"\ub0a8\uc131\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud0d1\uc2b9","wayPoints":[58,59]},{"distance":1995.2,"duration":143.7,"name":"\uc22d\uc2e4\ub300\uc785\uad6c (7\ud638\uc120)","type":"\uc22d\uc2e4\ub300\uc785\uad6c\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud0d1\uc2b9","wayPoints":[59,60]},{"distance":919.0,"duration":66.2,"name":"\uc0c1\ub3c4 (7\ud638\uc120)","type":"\uc0c1\ub3c4\uc5ed\uc5d0\uc11c 7\ud638\uc120 \ud0d1\uc2b9","wayPoints":[60,61]},{"distance":77.2,"duration":55.6,"name":"Head northwest","type":11,"wayPoints":[61,66]},{"distance":93.6,"duration":67.4,"name":"Turn left","type":0,"wayPoints":[66,68]},{"distance":10.6,"duration":7.6,"name":"Turn left","type":0,"wayPoints":[68,69]},{"distance":43.3,"duration":31.1,"name":"Turn right","type":1,"wayPoints":[69,70]},{"distance":158.6,"duration":114.2,"name":"Turn right","type":1,"wayPoints":[70,77]},{"distance":72.5,"duration":52.2,"name":"Turn right","type":1,"wayPoints":[77,79]},{"distance":572.9,"duration":412.5,"name":"Turn left","type":0,"wayPoints":[79,94]},{"distance":11.1,"duration":8.0,"name":"Turn slight left onto \ud751\uc11d\ub85c","type":4,"wayPoints":[94,95]},{"distance":20.9,"duration":15.0,"name":"Turn left onto \uc0c1\ub3c4\ub85c53\uae38","type":0,"wayPoints":[95,96]},{"distance":75.2,"duration":54.1,"name":"Turn right onto \uc0c1\ub3c4\ub85c47\uc544\uae38","type":1,"wayPoints":[96,99]},{"distance":228.1,"duration":164.2,"name":"Turn right onto \uc0c1\ub3c4\ub85c47\uc544\uae38","type":1,"wayPoints":[99,107]},{"distance":60.2,"duration":43.4,"name":"Turn left onto \uc0c1\ub3c4\ub85c47\uae38","type":0,"wayPoints":[107,109]},{"distance":264.6,"duration":190.5,"name":"Turn right onto \uc0c1\ub3c4\ub85c41\ub2e4\uae38","type":1,"wayPoints":[109,120]},{"distance":78.2,"duration":56.3,"name":"Turn right onto \uc0c1\ub3c4\ub85c37\uae38","type":1,"wayPoints":[120,121]},{"distance":51.4,"duration":37.0,"name":"Turn left onto \uc0c1\ub3c4\ub85c39\uae38","type":0,"wayPoints":[121,122]},{"distance":51.7,"duration":37.2,"name":"Turn right onto \uc0c1\ub3c4\ub85c, 90","type":1,"wayPoints":[122,124]},{"distance":0.0,"duration":0.0,"name":"Arrive at \uc0c1\ub3c4\ub85c, 90, on the left","type":10,"wayPoints":[124,124]}]}}]},"RESULT_MSG":"OK"},"status_number":200}
    with open('foo.json', 'w', encoding='utf8') as f:
        json.dump(foo, f, indent=4, ensure_ascii=False)

