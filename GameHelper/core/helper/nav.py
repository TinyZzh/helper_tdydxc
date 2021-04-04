# -*- encoding=utf8 -*-

from GameHelper.core.helper.aster import AStar
from typing import List
from enum import Enum
import sys
import math
import numpy as np


class NodeEnum(Enum):
    UNKNOWN = 0
    # 未知, 未探索的点.
    EMPTY = 1
    # 空地
    WALL = 2
    # 地图外
    NEXT_FLOOR = 3
    # 下一层
    SHOP = 4
    # 商店. 探索之后根据反馈确定
    CLICK_BLOCK = 5
    # 木箱子, 黄箱子，金箱子(操作), 宝石罐子, BUFF
    ALTAR = 6
    # 祭坛
    SPACE = 7
    # 秘境空间
    CLICK = 10
    # 除空地和地图之外的其他。可点击探索的。[怪物, 宝箱, 罐子, 下一层, ]
    GOLD_KEY_BOX = 11
    # 金钥匙箱
    DISPLAY_WAIT = 97
    # 显示 - 等待探索的点
    DISPLAY_PLAYER = 98
    # 地图玩家当前位置
    DISPLAY_ORIGIN = 99
    # 地图原始点. 仅显示时，使用


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
