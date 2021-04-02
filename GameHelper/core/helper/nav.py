# -*- encoding=utf8 -*-

from GameHelper.core.helper.aster import AStar
from typing import List
from enum import Enum
import sys
import math
import numpy as np


class NodeEnum(Enum):
    # 未知, 未探索的点.
    UNKNOWN = 0
    # 空地
    EMPTY = 1
    # 地图外
    WALL = 2
    # 下一层
    NEXT_FLOOR = 3
    # 商店. 探索之后根据反馈确定
    SHOP = 4
    # 木箱子, 黄箱子，金箱子(操作), 宝石罐子, BUFF
    CLICK_BLOCK = 5
    # 祭坛
    ALTAR = 6
    # 秘境空间
    SPACE = 7
    # 除空地和地图之外的其他。可点击探索的。[怪物, 宝箱, 罐子, 下一层, ]
    CLICK = 10
    # 地图玩家当前位置
    PLAYER = 98
    # 地图原始点. 仅显示时，使用
    ORIGIN = 99


class Node:
    x: int
    y: int
    state: NodeEnum

    def __init__(self, x=0, y=0, state=NodeEnum.UNKNOWN) -> None:
        self.x = x
        self.y = y
        self.state = state
        pass

    def __repr__(self) -> str:
        return "({},{},{})".format(self.x, self.y, self.state.name)

    def __iter__(self):
        return (v for v in [self.x, self.y, self.state])

