# -*- encoding=utf8 -*-

from GameHelper.core.helper.aster import AStar
from typing import Array, List
from enum import Enum
import sys
import math

class NodeEnum(Enum):
    #    
    NORMAL = 1
    # 障碍物 
    WALL = 2
    # 未知
    UNKNOWN = 3
    # 怪物
    MONSTER = 4
    # 3:BOSS   
    BOSS = 5
    # 宝石罐子
    GEN = 6
    # 宝箱
    BOX = 7
    # 下层入口
    NEXT = 8
    # 商店
    SHOP = 9


class Node:
    x: int
    y: int
    state: NodeEnum


class Navigation(AStar):
    # 导航组件. A*寻路. 引入隐藏地图格
    nodes: List[Node] = []

    def navigate(self, point) -> List[Node]:

        return

    def discover(self, data: List[Node]) -> None:

        return

    def has_unknown(self):
        for n in self.nodes:
            if n.state == NodeEnum.UNKNOWN:
                return True
        return False

    pass


class TiredMap:

    pass
