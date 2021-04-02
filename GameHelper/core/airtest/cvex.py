#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import types
from six import PY3
from copy import deepcopy

from airtest import aircv
from airtest.aircv import cv2
from airtest.core import cv
from airtest.core.helper import G, logwrap
from airtest.core.settings import Settings as ST  # noqa
from airtest.core.error import TargetNotFoundError, InvalidMatchingMethodError
from airtest.utils.transform import TargetPos


class AirImage(object):

    def __init__(self, origin_image, threshold=None, resolution=(), rgb=False) -> None:
        self.origin_image = origin_image
        self.threshold = threshold or ST.THRESHOLD
        self.resolution = resolution
        self.rgb = rgb

    def match(self, screen):
        match_result = self._cv_match(screen)
        G.LOGGING.debug("match result: %s", match_result)
        return match_result

    @logwrap
    def _cv_match(self, screen):
        # in case image file not exist in current directory:
        image = self.origin_image
        image = self._resize_image(image, screen, ST.RESIZE_METHOD)
        ret = None
        for method in ST.CVSTRATEGY:
            # get function definition and execute:
            func = cv.MATCHING_METHODS.get(method, None)
            print("func:{}".format(func))
            if func is None:
                raise InvalidMatchingMethodError("Undefined method in CVSTRATEGY: '%s', try 'kaze'/'brisk'/'akaze'/'orb'/'surf'/'sift'/'brief' instead." % method)
            else:
                ret = self._try_match(func, image, screen, threshold=self.threshold, rgb=self.rgb)
            if ret:
                break
        return ret

    @staticmethod
    def _try_match(func, *args, **kwargs):
        G.LOGGING.debug("try match with %s" % func.__name__)
        try:
            ret = func(*args, **kwargs).find_best_result()
        except aircv.NoModuleError as err:
            G.LOGGING.debug("'surf'/'sift'/'brief' is in opencv-contrib module. You can use 'tpl'/'kaze'/'brisk'/'akaze'/'orb' in CVSTRATEGY, or reinstall opencv with the contrib module.")
            return None
        except aircv.BaseError as err:
            G.LOGGING.debug(repr(err))
            return None
        else:
            return ret

    def _resize_image(self, image, screen, resize_method):
        """模板匹配中，将输入的截图适配成 等待模板匹配的截图."""
        # 未记录录制分辨率，跳过
        if not self.resolution:
            return image
        screen_resolution = aircv.get_resolution(screen)
        # 如果分辨率一致，则不需要进行im_search的适配:
        if tuple(self.resolution) == tuple(screen_resolution) or resize_method is None:
            return image
        if isinstance(resize_method, types.MethodType):
            resize_method = resize_method.__func__
        # 分辨率不一致则进行适配，默认使用cocos_min_strategy:
        h, w = image.shape[:2]
        w_re, h_re = resize_method(w, h, self.resolution, screen_resolution)
        # 确保w_re和h_re > 0, 至少有1个像素:
        w_re, h_re = max(1, w_re), max(1, h_re)
        # 调试代码: 输出调试信息.
        G.LOGGING.debug("resize: (%s, %s)->(%s, %s), resolution: %s=>%s" % (w, h, w_re, h_re, self.resolution, screen_resolution))
        # 进行图片缩放:
        image = cv2.resize(image, (w_re, h_re))
        return image
