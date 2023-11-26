from utils import *
from Astar_bus import *
from Astar_subway import *
from utils import *


def a_star_combined(map_subway, map_trans, map_bus, start_node, end_node, target_count=1):
    print(start_node.name, end_node.name)
    if start_node.type == end_node.type == "subway":
        return a_star_subway(map_subway, map_trans, start_node, end_node)
    elif start_node.type == end_node.type == "bus":
        return a_star_bus(map_bus, start_node, end_node)
    else:
        if start_node.type == "subway":
            children = []
            for new_nodes in map_trans:
                if map_trans[new_nodes]['id'] != start_node.id \
                        and map_trans[new_nodes]['name'] == start_node.name:
                    new_node = set_node_subway(map_subway[map_trans[new_nodes]['id']])
                    children.append(new_node)
            for new_nodes in start_node.adj:
                new_node = set_node_subway(map_subway[new_nodes['id']])
                node_position = (
                    map_subway[new_nodes['id']]['latitude'],  # X
                    map_subway[new_nodes['id']]['longitude'])  # Y

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
                children.append(new_node)
            for child in children:
                print(find_closest_transportation(map_bus, map_subway, [child.latitude, child.longitude])[0].name)
                if a_star_bus(map_bus, child, end_node) is not None:
                    return a_star_bus(map_bus, child, end_node).insert(
                        0, [start_node.name, [start_node.latitude, start_node.longitude]])

        elif start_node.type == "bus":
            children = []

            # adjacent nodes
            for new_nodes in start_node.adj:
                new_node = set_node_bus(map_bus[new_nodes['id']])
                node_position = (
                    map_bus[new_nodes['id']]['latitude'],  # X
                    map_bus[new_nodes['id']]['longitude'])  # Y

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
                children.append(new_node)
            for child in children:
                print(find_closest_transportation(map_bus, map_subway, [child.latitude, child.longitude])[1].name)
                if a_star_subway(map_subway, map_trans, child, end_node) is not None:
                    return a_star_subway(map_subway, map_trans, child, end_node).insert(
                        0, [start_node.name, [start_node.latitude, start_node.longitude]])
