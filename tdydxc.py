# -*- encoding=utf8 -*-

from GameHelper.core.helper import utility
from GameHelper.core.helper.aster import *
from enum import IntEnum
import math
from typing import List, Tuple
from GameHelper.core.helper.nav import Node, NodeEnum
from airtest.core.api import *
from airtest.aircv import *
import numpy as np


class Direction(IntEnum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4


class TdydxcGame:

    screen_center_point = None
    # 屏幕中心点坐标
    screen_point_cell_width = None
    # 游戏坐标格子宽度
    is_full_map = False
    # 全图模式. 有下一层入口时，不进入，等全图刷完
    is_debug = True
    # 调试模式. 开启更详细的日志
    game_not_moved_recheck_count = 2
    # 默认移动成果， 无法移动需要二次校验. 避免卡顿等误判情况
    game_touch_sleep = 2
    # 点击之后等到游戏响应的时间
    game_operation_delay = 1
    # 游戏内通用操作延迟. 1s
    game_auto_open_gold_key_box = False

    game_use_skill_recover_hp = 0.7
    # 血量低于70%使用技能回血

    # 是否自动打开金钥匙箱子
    buy_shop_item_list = []
    # 商店购买列表
    cur_floor = 1
    # 当前楼层

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
        self.current = np.array([51, 51])
        self._wait_nodes = []
        pass

    def get_nodes(self):
        self.map_draw()
        return self.map_nodes

    def init_mini_map(self, nodes: List[Node]) -> None:
        """初始化小地图. 帮助定位游戏坐标和导航.   小地图首行有地图信息遮挡、尾行有随机的大喇叭公告遮挡

        Args:
            nodes (List[Node]): [description]
        """
        _o_x, _o_y = self.current
        for (n_x, n_y, state) in nodes:
            x = _o_x + n_x
            y = _o_y + n_y
            self.map_nodes[x][y] = state.value
            if self.is_wait_discover_node((x, y)):
                self._wait_nodes.append((x, y))
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
        _datas = [p[0] for p in sorted(set(_datas), key=lambda p:p[1], reverse=False)]
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
            # print("point:{}, unknown border:{}, result:{}".format(point, _rounds, any(x == NodeEnum.UNKNOWN.value for x in _rounds)))
            return True

    def map_move(self, nodes: List[Node], direction: Direction) -> None:
        """游戏移动

        Args:
            nodes ([type]): [游戏小地图]
            direction (Direction): [方向]
        """
        # 移动之后, 同步坐标，同步小地图信息
        self.current += self.get_move_vector(direction)
        # self.__logger.info("after move current point:{}".format(self.current))
        if nodes:
            _o_x, _o_y = self.current
            for v_node in nodes:
                _r_x = _o_x + v_node.x
                _r_y = _o_y + v_node.y
                prev_state = self.map_nodes[_r_x][_r_y]
                if NodeEnum.UNKNOWN.value != prev_state:
                    self.__logger.info("discovered point:%s. prev:%s, current:%s", (_r_x, _r_y), NodeEnum(prev_state), v_node.state)
                    continue
                self.map_nodes[_r_x][_r_y] = v_node.state.value
                if self.is_wait_discover_node((_r_x, _r_y)):
                    self._wait_nodes.append((_r_x, _r_y))
                    pass
                pass
            self._resort_wait_nodes()
        pass

    def map_move_ex(self, nodes: List[Node], direction: Direction) -> None:
        """游戏移动, 长距离移动. 提高扫图效率

        Args:
            nodes ([type]): [游戏小地图]
            direction (Direction): [方向]
        """
        # 移动之后, 同步坐标，同步小地图信息
        self.current += self.get_move_vector(direction)
        # self.__logger.info("after move current point:{}".format(self.current))
        if nodes:
            _o_x, _o_y = self.current
            for v_node in nodes:
                _r_x = _o_x + v_node.x
                _r_y = _o_y + v_node.y
                prev_state = self.map_nodes[_r_x][_r_y]
                if NodeEnum.UNKNOWN.value != prev_state:
                    self.__logger.info("discovered point:%s. prev:%s, current:%s", (_r_x, _r_y), NodeEnum(prev_state), v_node.state)
                    continue
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
        npcs = [NodeEnum.EMPTY, NodeEnum.NEXT_FLOOR, NodeEnum.SHOP, NodeEnum.ALTAR, NodeEnum.SPACE, NodeEnum.GOLD_KEY_BOX]
        if state in npcs and (n.x, n.y) in self._wait_nodes:
            self._wait_nodes.remove((n.x, n.y))
            self.__logger.info("after discover: wait nodes: %s", self._wait_nodes)
            pass
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
            try:
                _display = (self.map_nodes[_min_x:_max_x, _min_y: _max_y]).copy()
                _display[self.current[0] - _min_x, self.current[1] - _min_y] = NodeEnum.DISPLAY_PLAYER.value
                _display[51 - _min_x, 51 - _min_y] = NodeEnum.DISPLAY_ORIGIN.value
                _dw = [(x-_min_x, y - _min_y) for x, y in self._wait_nodes]
                self.__logger.info("scene detail info. current:%s, wait nodes:%s, map:", self.current, self._wait_nodes)
                self.map_draw_ex(_display, _dw)
            except Exception as e:
                self.__logger.error("map draw failed. detail info. current:%s, init nodes:%s, rect:[%s, %s]", self.current, _nodes, (_min_x, _min_y), (_max_x, _max_y))
                self.map_draw_ex(_display)
                raise e
            pass
        pass

    def map_draw_ex(self, display, wait=[]) -> None:
        if wait:
            for i, j in wait:
                display[i][j] = NodeEnum.DISPLAY_WAIT.value
                pass
            pass
        # 翻转xy轴. 输出更直观的显示表格
        display = np.swapaxes(display, 0, 1)

        def map_icon(v) -> str:
            if v == NodeEnum.DISPLAY_ORIGIN.value:
                return "##"
            elif v == NodeEnum.DISPLAY_PLAYER.value:
                return "&&"
            elif v == NodeEnum.DISPLAY_WAIT.value:
                return "-W"
            elif v == NodeEnum.EMPTY.value:
                return "__"
            elif v in [NodeEnum.UNKNOWN.value, NodeEnum.WALL.value]:
                return "  "
            else:
                return "{:_>2d}".format(v)
            pass
        list(map(lambda row: self.__logger.info("|".join(map(map_icon, row))), display))
        pass

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

        def reachable(x, y):
            unreachable = [NodeEnum.WALL.value, NodeEnum.UNKNOWN.value, NodeEnum.ALTAR.value, NodeEnum.GOLD_KEY_BOX.value]
            # , NodeEnum.ALTAR.value
            # if self.map_nodes[x][y] == NodeEnum.NEXT_FLOOR.value and self.game.is_full_map:
            #     return self.is_map_clean()
            return self.map_nodes[x][y] not in unreachable

        return [(nx, ny) for nx, ny in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]if reachable(x, y)]

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
        if not self.is_map_clean():
            # 下一个探索点
            p = self._wait_nodes[0]
            pass
        if p is None:
            # 导航到下一层
            p = np.where(self.map_nodes == NodeEnum.NEXT_FLOOR.value)
            self.__logger.error("寻找下一层入口. current:{}, p:{}, nodes:{}".format(self.current, p, self._wait_nodes))
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
        self.__logger.error("毁灭性错误：无路可走. current:{}, p:{}, nodes:{}".format(self.current, p, self._wait_nodes))
        return None
    pass
