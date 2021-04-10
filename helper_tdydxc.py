# -*- encoding=utf8 -*-
__author__ = "TinyZ"


from tdydxc_game import do_endless_abyss, do_fetch_daily_task_reward, do_monster_iland
from GameHelper.core.airtest.cvex import AirImage
from GameHelper.core.helper.utility import Utility
from GameHelper.core.helper.nav import Node, NodeEnum
from GameHelper.core.util.ciede2000 import ciede2000
from airtest.core.api import *
from airtest.core.cv import loop_find
from airtest.aircv import *
from GameHelper.core.helper.images import get_pixel_color, hex_to_rgb, rgb_to_hex, screen_snapshot
from tdydxc import *
import tdydxc_map
from tdydxc_battle import *
from game_util import *


# 用户配置
class TdydxcConfig(object):


    game_scene_start = None
    # 初心试炼 - 挖掘场 - 噩梦模式 - 第一层

    def __init__(self) -> None:
        self.game_scene_start = (1, 3, 2, 1)
        pass

    def __repr__(self) -> str:
        return "(TdydxcConfig: {})".format(self.__dict__)

    pass

tdydxc_config = TdydxcConfig()

tdydxc_actions = [
    do_monster_iland,
    do_endless_abyss,
    do_fetch_daily_task_reward,

]

while True:
    try:
        for action in tdydxc_actions:
            action()
            pass
    except Exception as e:
        Utility.LOGGER.warn("执行任务失败. %s", e)
        pass
    pass

# import time
# snapshot(msg="请填写测试点.", filename="aaa-{}.png".format(time.time()))

do_fetch_daily_task_reward()
# touch(Template(r"tpl1616073759155.png", record_pos=(-0.079, 0.475), resolution=(720, 1280)))
# # 初心试炼 - 挖掘场 - 噩梦模式 - 第一层
# # on_select_battle_map(1, 3, 2, 1)
# on_select_battle_map(2, 3, 1, 1)
# # aircv.show_origin_size(snapshot_mini_map())
# on_battle_change_bonfire()
# sleep(3)
# on_auto_battle()
aircv.show_origin_size(snapshot_mini_map())
###############################################
##             自动选择关卡                  ###
###############################################



# 搜索右上角小地图. 确定黑色不可行动的区域.  12*12
# lookup(, (530, 30, 720, 190))


# print(loop_find(Template(r"tpl1616404376736.png", record_pos=(0.438, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404431747.png", record_pos=(0.365, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404419462.png", record_pos=(0.324, -0.797), resolution=(720, 1280))))








