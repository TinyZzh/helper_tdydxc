# -*- encoding=utf8 -*-

from GameHelper.core.helper import utility
from GameHelper.core.helper.aster import *
from enum import IntEnum
import math
from typing import List, Tuple
from GameHelper.core.helper.nav import Node, NodeEnum
from GameHelper.core.util.ciede2000 import ciede2000
from airtest.core.api import *
from airtest.aircv import *
from GameHelper.core.helper.images import find_multi_color_ex, get_multi_color, get_pixel_color, hex_to_rgb, rgb_to_hex, screen_snapshot
import numpy as np


class Direction(IntEnum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4


class TdydxcGame:

    # 屏幕中心点坐标
    screen_center_point = None
    # 游戏坐标格子宽度
    screen_point_cell_width = None
    # 全图模式. 有下一层入口时，不进入，等全图刷完
    is_full_map = True
    # 商店购买列表
    buy_shop_item_list = []
    # 当前楼层
    cur_floor = 1

    def __repr__(self) -> str:
        return "(TdydxcGame: {})".format(self.__dict__)
    pass


class TdydxcScene(AStar):

    __logger = utility.get_logger(__name__)
    # 提灯与地下城的场景逻辑地图信息
    map_nodes = np.array([])
    # 初始逻辑坐标[51, 51]坐标系中心点
    current = np.array([51, 51])

    game: TdydxcGame = None
    # 未知格子. 等待点击探索
    _wait_nodes: List[Tuple[int, int]] = []

    def __init__(self) -> None:
        # 初始化[50*50]地图格子
        self.map_nodes = np.zeros((101, 101), np.dtype(np.int8))
        pass

    def get_nodes(self):
        self.map_draw()
        return self.map_nodes

    def parse_mini_map(self, mini_map, offset=(5, 3)) -> tuple:
        _nodes = np.zeros([11, 9], dtype=np.int32)
        for x in range(-5, 6):
            for y in range(-3, 5):
                v_node = self.get_map_node(mini_map, (x, y))
                _r_x = offset[0] + x
                _r_y = offset[1] + y
                _nodes[_r_x][_r_y] = v_node.state.value
                pass
            pass
        return _nodes

    def init_mini_map(self, mini_map) -> None:
        # 初始化小地图. 帮助定位游戏坐标和导航.   小地图首行有地图信息遮挡、尾行有随机的大喇叭公告遮挡
        h, w = mini_map.shape[:2]
        cx = cy = _cp = int(w / 2)
        _o_x, _o_y = self.current
        aircv.mark_point(mini_map, (cx, cy), circle=True, radius=1)
        for x in range(-5, 6):
            for y in range(-3, 5):
                v_node = self.get_map_node(mini_map, (x, y))
                _r_x = _o_x + x
                _r_y = _o_y + y
                self.map_nodes[_r_x][_r_y] = v_node.state.value
                if self.is_wait_discover_node((_r_x, _r_y)):
                    self._wait_nodes.append((_r_x, _r_y))
                    pass
                pass
            pass
        # 中心是玩家当前位置
        self.map_nodes[_o_x][_o_y] = NodeEnum.EMPTY.value
        self._resort_wait_nodes()
        return

    def _resort_wait_nodes(self) -> None:
        # 根据距离排序待搜索的目标点.
        # 根据寻路算法结果排序， 寻找最优解
        _datas = []
        _origin = tuple(self.current)
        for vn in self._wait_nodes:
            if self.is_wait_discover_node(vn):
                # 未探索的点
                vn_size = len(self.lookup_path(_origin, vn))
                if vn_size > 0:
                    # 可以寻路到达的点.
                    # 地图未探索完全，导致导航算法无法导航
                    _datas.append((vn, vn_size))
                    pass
                pass
            pass
        _datas = [p[0] for p in sorted(_datas, key=lambda p:p[1], reverse=False)]
        self._wait_nodes = _datas
        pass

    def is_wait_discover_node(self, point) -> bool:
        """是否等待探索的节点

        Args:
            point ([type]): [description]

        Returns:
            bool: [description]
        """
        mn = self.map_nodes
        x, y = point
        if mn[x][y] == NodeEnum.CLICK.value:
            return True
        elif mn[x][y] == NodeEnum.WALL.value:
            # 墙. 不需要探索
            return False
        elif mn[x][y] == NodeEnum.EMPTY.value:
            # 地图边缘的空地，需要探索
            _rounds = [mn[x-1][y], mn[x+1][y], mn[x][y-1], mn[x][y+1]]
            r = any(x == NodeEnum.UNKNOWN.value for x in _rounds)
            return r
        else:
            # 其他情况, 保险起见加入待查队列
            _rounds = [mn[x-1][y], mn[x+1][y], mn[x][y-1], mn[x][y+1]]
            print("point:{}, unknown border:{}, result:{}".format(
                point, _rounds, any(x == NodeEnum.UNKNOWN.value for x in _rounds)))
            return True

    def get_click_point(self, direction: Direction) -> Node:
        p = tuple(self.current + self.get_move_vector(direction))
        return Node(p[0], p[1], NodeEnum(self.map_nodes[p[0], p[1]]))

    def get_move_vector(self, direction: Direction) -> tuple:
        if direction == Direction.TOP:
            return np.array([0, -1])
        elif direction == Direction.BOTTOM:
            return np.array([0, 1])
        elif direction == Direction.RIGHT:
            return np.array([1, 0])
        else:
            return np.array([-1, 0])

    def _map_p(self, v) -> int:
        # 根据中心点(90, 90)和相对坐标，计算屏幕位置  分辨率:[720, 1280]
        return 90 + 17 * v

    def map_draw_rectangle(self, image, point) -> any:
        _p_x, _p_y = point
        x = self._map_p(_p_x)
        y = self._map_p(_p_y)
        self.__logger.info("%s, %s", (x-8, y-8), (x+8, y+8))
        # 255：蓝色
        cv2.rectangle(image, (x-8, y-8), (x+8, y+8), 0, -1)
        return image

    def _map_multi_point(self, point) -> int:
        # [中, 上, 左, 右]
        _p_x, _p_y = point
        x = self._map_p(_p_x)
        y = self._map_p(_p_y)
        return [(x, y), (x, y - 5), (x-2, y+2), (x+2, y+2)]

    def get_map_node(self, mini_map, point) -> Node:
        # 识别根据小地图. 识别地图点.
        x, y = point
        _p_x = self._map_p(x)
        _p_y = self._map_p(y)
        try:
            _cell = None
            # self.__logger.info("rgb:{}, black like:{}".format(_rgb, ciede2000(lab1=_rgb, lab2=_black)))
            _multi_points = self._map_multi_point(point)
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
                # self.__logger.debug("xxx: {} - {} - {}".format(v_clr_hex, v_state, clr_points))
                if find_multi_color_ex(mini_map, points=clr_points, threshold=15):
                    _cell = v_state
                    # self.__logger.debug("match point:{}, rgb:{}, state:{}".format(point, v_clr_hex, v_state))
                    break
                pass
            if not _cell:
                # 未知的点, 直接认为可点击
                self.__logger.debug("not sure node type. p:{}, rgb:{}, ".format(point, list(map(rgb_to_hex, get_multi_color(mini_map, _multi_points)))))
                _cell = NodeEnum.CLICK
                pass
            aircv.mark_point(mini_map, (_p_x, _p_y), radius=1)
            pass
        except Exception as e:
            self.__logger.error("get_map_node. msg:{}. point:{}, map:[{}, {}]".format(e, point, _p_x, _p_y))
            # aircv.show_origin_size(mini_map)
            raise e
        return Node(x, y, _cell)

    def map_move(self, nodes: List[Node], direction: Direction) -> None:
        """游戏移动

        Args:
            nodes ([type]): [游戏小地图]
            direction (Direction): [方向]
        """
        # 移动之后, 同步坐标，同步小地图信息
        self.current += self.get_move_vector()
        self.__logger.info("after move current point:{}".format(self.current))
        if nodes:
            _o_x, _o_y = self.current
            for v_node in nodes:
                _r_x = _o_x + v_node.x
                _r_y = _o_y + v_node.y
                self.map_nodes[_r_x][_r_y] = v_node.state.value
                if self.is_wait_discover_node((_r_x, _r_y)):
                    self._wait_nodes.append((_r_x, _r_y))
                    pass
                pass
            self._resort_wait_nodes()
        pass

    def map_discover(self, direction: Direction, state: NodeEnum) -> None:
        """探索坐标点. 宝箱、宝石罐等探索之后需要更新地图信息

        Args:
            direction (Direction): [description]
            state (NodeEnum): [description]
        """
        n: Node = self.get_click_point(direction)
        self.map_nodes[n.x][n.y] = state.value
        # 以探索的节点， 移除掉探索点
        npcs = [NodeEnum.EMPTY, NodeEnum.NEXT_FLOOR, NodeEnum.SHOP, NodeEnum.ALTAR]
        if state in npcs and (n.x, n.y) in self._wait_nodes:
            self._wait_nodes.remove((n.x, n.y))
        return

    def map_draw(self) -> None:
        rx, ry = np.where(self.map_nodes != NodeEnum.UNKNOWN.value)
        _nodes = tuple(np.c_[rx, ry])
        if _nodes:
            _min_x = int(min(_nodes, key=lambda n: n[0])[0] - 1)
            _max_x = int(max(_nodes, key=lambda n: n[0])[0] + 2)
            _min_y = int(min(_nodes, key=lambda n: n[1])[1] - 1)
            _max_y = int(max(_nodes, key=lambda n: n[1])[1] + 2)
            # 有效区域内的点
            _display = (self.map_nodes[_min_x:_max_x, _min_y: _max_y]).copy()
            _display[self.current[0] - _min_x, self.current[1] - _min_y] = NodeEnum.PLAYER.value
            _display[51 - _min_x, 51 - _min_y] = NodeEnum.ORIGIN.value
            # 翻转xy轴. 输出更直观的显示表格
            _display = np.swapaxes(_display, 0, 1)

            def map_icon(v) -> str:
                if v == NodeEnum.ORIGIN.value:
                    return "##"
                elif v == NodeEnum.PLAYER.value:
                    return "&&"
                elif v not in [NodeEnum.UNKNOWN.value, NodeEnum.WALL.value]:
                    return "{:_>2d}".format(v)
                else:
                    return "__"
                pass
            self.__logger.info("scene map:")
            list(map(lambda row: self.__logger.info("|".join(map(map_icon, row))), _display))
            pass
        if self._wait_nodes:
            self.__logger.info("scene wait node:{}".format(self._wait_nodes))
            pass
        pass

    def map_draw_ex(self, display) -> None:
        display = np.swapaxes(display, 0, 1)

        def map_icon(v) -> str:
            if v == NodeEnum.ORIGIN.value:
                return "##"
            elif v == NodeEnum.PLAYER.value:
                return "&&"
            elif v not in [NodeEnum.UNKNOWN.value, NodeEnum.WALL.value]:
                return "{:_>2d}".format(v)
            else:
                return "__"
            pass
        list(map(lambda row: self.__logger.info("|".join(map(map_icon, row))), display))
        pass

    def get_screen_point(self, direction: Direction) -> tuple:
        """获取方向获取屏幕中点击的点坐标

        Args:
            direction (Direction): [移动的方向]

        Returns:
            [type]: [description]
        """
        w = self.game.screen_point_cell_width
        x, y = self.game.screen_center_point
        vec_x = -1 if direction == Direction.LEFT else 1 if direction == Direction.RIGHT else 0
        vec_y = -1 if direction == Direction.TOP else 1 if direction == Direction.BOTTOM else 0
        return (x + vec_x * w, y + vec_y * w)

    # AStar寻路算法

    def heuristic_cost_estimate(self, n1, n2):
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        x, y = node
        unreachable = [NodeEnum.WALL.value, NodeEnum.UNKNOWN.value, NodeEnum.ALTAR.value]
        return [(nx, ny) for nx, ny in [(
            x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]if self.map_nodes[nx][ny] not in unreachable]

    def lookup_path(self, start, goal) -> List:
        """寻路算法

        Args:
            start ([type]): [description]
            goal ([type]): [description]

        Returns:
            List: [description]
        """
        try:
            _list = self.astar(start=start, goal=goal)
            _list = list(map(tuple, _list)) if _list else []
            # self.__logger.info("lookup_path[{} -> {}], path:{}, len:{}".format(start, goal, _list, len(_list)))
            return _list
        except Exception as e:
            self.__logger.warning("lookup_path[{} -> {}], e:{}".format(start, goal, e))
            return []

    def is_map_clean(self) -> bool:
        return len(self._wait_nodes) <= 0

    def nav_next_point(self) -> tuple:
        p = None
        if self._wait_nodes:
            # 下一个探索点
            p = self._wait_nodes[0]
        else:
            # 导航到下一层
            p = np.where(self.map_nodes != NodeEnum.NEXT_FLOOR.value)
            pass
        if p:
            _path = self.lookup_path(tuple(self.current), p)
            if _path and len(_path) > 1:
                vec_x, vec_y = np.array(_path[1]) - self.current
                if vec_x == 0:
                    return Direction.TOP if vec_y < 0 else Direction.BOTTOM
                else:
                    return Direction.LEFT if vec_x < 0 else Direction.RIGHT
                    pass
                pass
            pass
        self.__logger.error("未找到下一个行动点. current:{}".format(self.current))
        return None
    pass