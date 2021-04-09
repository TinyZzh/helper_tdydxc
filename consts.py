# -*- encoding=utf8 -*-

from airtest.core.api import *

class Consts(object):

    TPL_SHEN_YUAN_RU_KOU = Template(r"tpl1616073759155.png", record_pos=(-0.079, 0.475), resolution=(720, 1280))
    """深渊入口
    """
    TPL_BTN_CONFIRM = Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440))
    """确定按钮
    """
    TPL_BTN_CANCEL = Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280))
    """取消按钮
    """
    TPL_BTN_QUIT = Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280))
    """退出按钮
    """
    TPL_MAP_1 = Template(r"tpl1617543743636.png", record_pos=(0.268, -0.411), resolution=(720, 1280))
    """绿先知林地
    """
    TPL_MAP_2 = Template(r"tpl1617543749731.png", record_pos=(-0.256, -0.182), resolution=(720, 1280))
    """利爪蛇巢穴
    """
    TPL_MAP_3 = Template(r"tpl1617543758666.png", record_pos=(0.268, 0.028), resolution=(720, 1280))
    """巨魔挖掘场
    """
    TPL_MAP_4 = Template(r"tpl1617543763794.png", record_pos=(-0.272, 0.243), resolution=(720, 1280))
    """龙骨熔岩
    """
    TPL_MAP_5 = Template(r"tpl1617543772341.png", record_pos=(0.229, 0.461), resolution=(720, 1280))
    """暗夜城堡
    """
    TPL_MAP_DIFF_1 = Template(r"tpl1617543789134.png", record_pos=(-0.001, -0.185), resolution=(720, 1280), rgb=True)
    """普通难度
    """
    TPL_MAP_DIFF_2 = Template(r"tpl1617543822397.png", record_pos=(-0.001, -0.192), resolution=(720, 1280), rgb=True)
    """噩梦难度
    """
    TPL_MAP_LEVEL_1 =  Template(r"tpl1617543847863.png", record_pos=(-0.01, -0.013), resolution=(720, 1280)),
    """1层
    """
    TPL_MAP_LEVEL_2 =  Template(r"tpl1617543857853.png", record_pos=(-0.008, 0.138), resolution=(720, 1280)),
    """11层
    """
    TPL_MAP_LEVEL_3 =  Template(r"tpl1617543864919.png", record_pos=(0.01, 0.296), resolution=(720, 1280)),
    """21层
    """
    TPL_MAP_LEVEL_4 =  Template(r"tpl1617543873441.png", record_pos=(0.001, 0.46), resolution=(720, 1280)),
    """直接BOSS
    """


    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise Exception("can't change const %s" % name)
        if not name.isupper():
            raise Exception('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value
        pass

tx = Consts()
