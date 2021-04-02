# -*- encoding=utf8 -*-

from tdydxc import Direction
from GameHelper.core.helper.utility import Utility
from GameHelper.core.helper.nav import Node, NodeEnum
from airtest.core.api import *
from airtest.aircv import *
from GameHelper.core.helper.images import find_multi_color_ex, get_multi_color, hex_to_rgb, rgb_to_hex
import numpy as np

__logger__ = Utility.LOGGER

def map_pixel_point(v) -> int:
    # 根据中心点(90, 90)和相对坐标，计算屏幕位置  分辨率:[720, 1280]
    return 90 + 17 * v

def get_icon_feature_points(point) -> int:
    # [中, 上, 左, 右]
    x = y = map_pixel_point(point[0])
    return [(x, y), (x, y - 5), (x-2, y+2), (x+2, y+2)]

def map_draw_rectangle(image, point) -> any:
    _p_x, _p_y = point
    x = map_pixel_point(_p_x)
    y = map_pixel_point(_p_y)
    __logger__.info("%s, %s", (x-8, y-8), (x+8, y+8))
    # 255：蓝色
    cv2.rectangle(image, (x-8, y-8), (x+8, y+8), 0, -1)
    return image

def map_node_recognition_with_direction(mini_map, direction: Direction) -> any:
    if direction == Direction.TOP:
        return list(map_node_recognition(mini_map, (i, -3)) for i in range(-5, 6))
    elif direction == Direction.BOTTOM:
        return list(map_node_recognition(mini_map, (i, 4)) for i in range(-5, 6))
    elif direction == Direction.RIGHT:
        return list(map_node_recognition(mini_map, (5, i)) for i in range(-3, 5))
    else:
        return list(map_node_recognition(mini_map, (-5, i)) for i in range(-3, 5))

def map_node_recognition(mini_map, point, mark_point=False) -> Node:
    """小地图节点识别. 根据特征点颜色识别地图格子的类型.

    Args:
        mini_map ([type]): [description]
        point ([type]): [description]

    Raises:
        e: [description]

    Returns:
        Node: [description]
    """
    # 识别根据小地图. 识别地图点.
    x, y = point
    _p_x = map_pixel_point(x)
    _p_y = map_pixel_point(y)
    try:
        _cell = None
        # __logger.info("rgb:{}, black like:{}".format(_rgb, ciede2000(lab1=_rgb, lab2=_black)))
        _multi_points = get_icon_feature_points(point)
        _kps = {
            '黑  色': (['#000000', '#000000', '#000000', '#000000'], NodeEnum.WALL),
            '空  地': (['#1B3A42', '#1B3A42', '#1B3A42', '#1B3A42'], NodeEnum.EMPTY),
            'BUFF ': (['#15272b', '#123038', '#b6c5cc', '#90929f'], NodeEnum.CLICK_BLOCK),
            '木  箱': (['#8e6048', '#212e1a', '#704c40', '#83685d'], NodeEnum.CLICK_BLOCK),
            # '木  箱': (['#896742', '#0f0a11', '#a5715b', '#945b54'], NodeEnum.CLICK_BLOCK),
            '宝  箱': (['#461e00', '#3d3006', '#b2945e', '#ad966d'], NodeEnum.CLICK_BLOCK),
            '宝  箱': (['#461e00', '#3d3006', '#b2945e', '#ad966d'], NodeEnum.CLICK_BLOCK),
            '宝  箱': (['#855d3a', '#000a0d', '#94655d', '#815c4a'], NodeEnum.CLICK_BLOCK),
            # '宝石罐': (['#6f3215'], NodeEnum.CLICK_BLOCK),
            # '秘  境': (['#25628f', '#638390', '#2d4b63', '#29414b'], NodeEnum.SPACE),
            '秘  境': (['#486b93', '#6e8a96', '#3c6488', '#344e5f'], NodeEnum.SPACE),
        }
        for v_clr_hex, v_state in _kps.values():
            clr_points = [(_multi_points[i][0], _multi_points[i][1], hex_to_rgb(v_clr_hex[i])) for i in range(len(_multi_points))]
            # __logger__.debug("xxx: {} - {} - {}".format(v_clr_hex, v_state, clr_points))
            if find_multi_color_ex(mini_map, points=clr_points, threshold=15):
                _cell = v_state
                # __logger.debug("match point:{}, rgb:{}, state:{}".format(point, v_clr_hex, v_state))
                break
            pass
        if not _cell:
            # 未知的点, 直接认为可点击
            __logger__.debug("not sure node type. p:{}, rgb:{}, ".format(point, list(map(rgb_to_hex, get_multi_color(mini_map, _multi_points)))))
            _cell = NodeEnum.CLICK
            pass
        if mark_point:
            aircv.mark_point(mini_map, (_p_x, _p_y), radius=1)
            pass
        pass
    except Exception as e:
        __logger__.error("map_node_recognition. msg:{}. point:{}, map:[{}, {}]".format(e, point, _p_x, _p_y))
        # aircv.show_origin_size(mini_map)
        raise e
    return Node(x, y, _cell)

def parse_mini_map(mini_map, offset=(5, 3), mark_point=False) -> tuple:
    if mark_point:
        h, w = mini_map.shape[:2]
        cx = cy = int(w / 2)
        aircv.mark_point(mini_map, (cx, cy), circle=True, radius=1)
        pass
    _nodes = np.zeros([11, 9], dtype=np.int32)
    for x in range(-5, 6):
        for y in range(-3, 5):
            v_node = map_node_recognition(mini_map, (x, y), mark_point)
            _r_x = offset[0] + x
            _r_y = offset[1] + y
            _nodes[_r_x][_r_y] = v_node.state.value
            pass
        pass
    return _nodes

def init_mini_map(mini_map) -> None:
    # 初始化小地图. 帮助定位游戏坐标和导航.   小地图首行有地图信息遮挡、尾行有随机的大喇叭公告遮挡
    h, w = mini_map.shape[:2]
    cx = cy = _cp = int(w / 2)
    _o_x, _o_y = current
    aircv.mark_point(mini_map, (cx, cy), circle=True, radius=1)
    for x in range(-5, 6):
        for y in range(-3, 5):
            v_node = map_node_recognition(mini_map, (x, y))
            _r_x = _o_x + x
            _r_y = _o_y + y
            map_nodes[_r_x][_r_y] = v_node.state.value
            if is_wait_discover_node((_r_x, _r_y)):
                _wait_nodes.append((_r_x, _r_y))
                pass
            pass
        pass
    # 中心是玩家当前位置
    map_nodes[_o_x][_o_y] = NodeEnum.EMPTY.value
    _resort_wait_nodes()
    return