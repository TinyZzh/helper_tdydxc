# -*- encoding=utf8 -*-

from GameHelper.core.helper.images import is_color_similar
from airtest.core.api import *
from tdydxc_battle import *
from consts import *


def do_monster_iland() -> None:
    """怪兽岛迷宫
    """
    swipe(Template(r"tpl1617967648305.png", record_pos=(-0.339, 0.1), resolution=(720, 1280)), vector=[0.7279, 0.0])
    touch(Template(r"tpl1617967677703.png", record_pos=(-0.392, -0.349), resolution=(720, 1280)))
    touch(Template(r"tpl1617967684718.png", record_pos=(-0.104, -0.246), resolution=(720, 1280)))
    if exists(Template(r"tpl1617967726031.png", record_pos=(-0.176, -0.056), resolution=(720, 1280))):
        touch(consts.tx.TPL_BTN_CANCEL)
        pass
    # 进入怪兽岛
    on_auto_battle()

    pass


def do_endless_abyss() -> None:
    """无尽深渊
    """
    swipe(Template(r"tpl1617967648305.png", record_pos=(-0.339, 0.1), resolution=(720, 1280)), vector=[0.7279, 0.0])
    touch(Template(r"tpl1617967677703.png", record_pos=(-0.392, -0.349), resolution=(720, 1280)))
    touch(Template(r"tpl1617968096714.png", record_pos=(0.001, 0.086), resolution=(720, 1280)))
    if exists(Template(r"tpl1617967726031.png", record_pos=(-0.176, -0.056), resolution=(720, 1280))):
        touch(consts.tx.TPL_BTN_CANCEL)
        pass
    # 进入无尽深渊
    on_auto_battle()
    pass


def do_fetch_daily_task_reward() -> None:
    """每日任务是否完成. 完成并领取奖励.
    滚动公告会导致识别不准确
    """
    while True:
        try:
            tpl_daily_task_tips = Template(r"tpl1617969337619.png", rgb=True, target_pos=7, record_pos=(0.422, -0.561), resolution=(720, 1280))
            match_pos = exists(tpl_daily_task_tips)
            if not match_pos:
                break
            touch(match_pos)
            img = device().snapshot()
            completed = all([is_color_similar(img, (x, y), clr, 10) for x, y, clr in [(385, 583, '#617339'), (385, 592, '#636f3f')]])
            if not completed:
                break
            touch((522, 573))
            touch(consts.tx.TPL_BTN_CONFIRM)
            touch(consts.tx.TPL_BTN_QUIT)
            pass
        except Exception as e:
            Utility.LOGGER.error("daily task failure. %s", e)
            pass
        else:
            break
    pass
