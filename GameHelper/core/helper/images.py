# -*- encoding=utf8 -*-

from typing import List, Tuple
from airtest.aircv import *
from GameHelper.core.util.ciede2000 import ciede2000
import math


def screen_snapshot(screen, rect) -> object:
    # 截取部分图片. [左上角x, y, 右下角x, y]
    return aircv.crop_image(screen, rect)


def rgb_to_hex(rgb):
    # RGB转颜色
    return '#%02x%02x%02x' % rgb


def hex_to_rgb(value: str) -> tuple:
    # 颜色 `#FFFFFF` -> ()
    value = value.lstrip('#')
    return list(int(value[i:i+2], 16) for i in (0, 2, 4))


def get_pixel_color(image, point) -> str:
    # 位于屏幕中[x, y]位置的点的rgb值的获取：(x,y均从0计数)
    # 注意：这里拿到的颜色是bgr，而非rgb
    x, y = point
    bgr = image[y][x]
    return tuple(bgr[..., ::-1])


def get_multi_color(image, points) -> str:
    # 位于屏幕中[x, y]位置的点的rgb值的获取：(x,y均从0计数)
    # 注意：这里拿到的颜色是bgr，而非rgb
    return list(map(lambda p: get_pixel_color(image, p), points))


def find_multi_color_ex(image, threshold: float = 10, points=[]) -> List:
    """匹配多颜色点，并返回首个坐标点

    Args:
        image ([type]): [description]
        threshold (float, optional): [description]. Defaults to 0.70.
        points (list, optional): [description]. Defaults to [].

    Returns:
        List: [description]
    """
    for x, y, rgb in points:
        _rgb = get_pixel_color(image, (x, y))
        if ciede2000(lab1=_rgb, lab2=rgb) > threshold:
            return None
        pass
    return points[0]
