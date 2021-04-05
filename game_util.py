# -*- encoding=utf8 -*-


from airtest.core.api import *
from GameHelper.core.helper.images import screen_snapshot


def game_snapshot(rect=None):
    """游戏截图

    Args:
        rect ([type], optional): [截取指定左上角和右下角坐标的图]. Defaults to None.

    Returns:
        [type]: [description]
    """
    _device = device()
    if not rect or len(rect) < 4:
        return snapshot()
    _screen = _device.snapshot()
    return screen_snapshot(_screen, rect)
