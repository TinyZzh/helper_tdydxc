# -*- encoding=utf8 -*-

from typing import List, Tuple
from airtest.aircv import *
from GameHelper.core.util import langs


def screen_snapshot(screen, rect) -> object:
    # 截取部分图片. [左上角x, y, 右下角x, y]
    return aircv.crop_image(screen, rect)


def get_pixel_color(image, point) -> str:
    # 位于屏幕中[x, y]位置的点的rgb值的获取：(x,y均从0计数)
    # 注意：这里拿到的颜色是bgr，而非rgb
    x, y = point
    bgr = image[y][x]
    return bgr[...,::-1]


def find_multi_color_ex(image, threshold=0.7, *args, **kwargs) -> List:
    _result = []
    if langs.is_iterable(args):
        for p in args:
            _result.append(get_pixel_color(image, p))
            pass
        pass
    return _result


