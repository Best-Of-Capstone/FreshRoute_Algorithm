from utils import *


def a_star_bus(map, start, end):
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
                path.append([current.name, [current.latitude, current.longitude]])
                # path.append([current.latitude, current.longitude])
                current = current.parent
            return path[::-1]  # reverse

        children = []

        # transfer nodes
        trans_tmp = []
        for new_nodes in trans:
            if trans[new_nodes]['id'] != current_node.id \
                    and trans[new_nodes]['name'] == current_node.name:
                new_node = set_node(map[trans[new_nodes]['id']])
                children.append(new_node)

        # adjacent nodes
        for new_nodes in (current_node.adj or trans_tmp):
            new_node = set_node(map[new_nodes['id']])
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
            children.append(new_node)

        for new_nodes in trans_tmp:
            print(new_nodes.id, new_nodes.name)

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