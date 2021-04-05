# -*- encoding=utf8 -*-
__author__ = "TinyZ"


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


tdydxc_conf = {

}


class HandleResult(object):

    match_pos = None
    # 图片识别匹配命中的坐标
    moved = False
    # 是否发生移动

    def __init__(self, match_pos, moved) -> None:
        self.match_pos = match_pos
        self.moved = moved
        pass

    def __repr__(self) -> str:
        return "HandleResult. pos:{}, moved:{}".format(self.match_pos, self.moved)


def snapshot_mini_map(rect=[532, 8, 712, 188]):
    # 获取小地图截图
    _screen = device().snapshot()
    return screen_snapshot(_screen, rect)

# [90*90]图片
# before_mini_map = snapshot_mini_map([571, 47, 673, 149])
# Utility.LOGGER.error("匹配结果: %s", AirImage(before_mini_map).match(before_mini_map))
# aircv.show_origin_size(before_mini_map)


def on_game_move_ex2(scene: TdydxcScene, direction: Direction) -> None:
    before_snapshot = snapshot_mini_map()
    # aircv.show_origin_size(before_snapshot)
    rel_p = scene.get_screen_point(direction)
    touch(rel_p)
    # note: 点击之后，模拟器卡顿后。会导致本次识别是否移动错误
    sleep(scene.game.game_touch_sleep)
    hr = None
    # 是否弹出交互界面
    node = scene.get_click_point(direction)
    Utility.LOGGER.info("start move. current:%s, click:%s", scene.current, node)

    node_handlers = {
        NodeEnum.NEXT_FLOOR.name: on_handle_next_floor,
        NodeEnum.ALTAR.name: on_handle_altar,
        NodeEnum.SPACE.name: on_handle_sercet_space,
        NodeEnum.GOLD_KEY_BOX.name: on_handle_gold_box,
        NodeEnum.SHOP.name: on_handle_shop,
    }

    if node.state == NodeEnum.CLICK:
        handlers = [
            on_handle_battle,
            on_handle_next_floor,
            on_handle_altar,
            on_handle_sercet_space,
            on_handle_gold_box,
            on_handle_shop,
            on_handle_unknown_node,
        ]
        _kw = {}
        for h in handlers:
            hr = h(scene, direction, image=before_snapshot)
            if hr:
                Utility.LOGGER.info("handle event:%s, direction:%s", h, direction)
                break
            pass
        pass
    elif node.state in node_handlers:
        node_handlers[node.state.name](scene, direction, image=before_snapshot)
        pass

    check_moved = False if isinstance(hr, HandleResult) and not hr.moved else True
    if check_moved:
        # 判断是否移动成功
        # 地图点变化超过6个， 判定为已移动
        def is_player_moved(orogin_nodes, count) -> any:
            img = snapshot_mini_map()
            cur_nodes = tdydxc_map.parse_mini_map(img)
            w, h = orogin_nodes.shape
            # if scene.game.is_debug:
            #     scene.map_draw_ex(orogin_nodes)
            #     scene.map_draw_ex(cur_nodes)
            #     pass
            diff = sum([1 if orogin_nodes[i][j] != cur_nodes[i][j] else 0 for i in range(w) for j in range(h)])
            Utility.LOGGER.error("地图差异情况统计：diff:%s, shape:%s, index:%d", diff, (w, h), (count+1))
            if diff < 5:
                return None
            return img

        before_nodes = tdydxc_map.parse_mini_map(before_snapshot)
        after_snapshot = None
        for i in range(scene.game.game_not_moved_recheck_count):
            after_snapshot = is_player_moved(before_nodes, i)
            if after_snapshot is not None:
                break
            # 等待2s后再校验一次.
            sleep(scene.game.game_operation_delay)
            log("tdydxc. current:{}, click:{}".format(scene.current, node), timestamp=time.time(), desc="判断是否移动", snapshot=True)
            pass
        if after_snapshot is not None:
            # 等待移动完成. 优化一下判断逻辑. 有可能卡住导致移动失败
            scene.map_move(tdydxc_map.map_node_recognition_with_direction(after_snapshot, direction), direction)
            pass
        pass

    scene.map_draw()
    # aircv.show_origin_size(after_snapshot)
    pass


def on_handle_battle(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> any:
    pos = exists(Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280)))
    if pos:
        # 进入战斗, 等待战斗胜利.
        # 有可能出现秒杀，耗时短, 必须优先判断
        on_game_battle(scene)
        scene.map_discover(direction, NodeEnum.EMPTY)
        return HandleResult(pos, False)
    return pos


def on_handle_basic_dialog(tpl_wait: Template, func_suc, func_fail=None, lmt_operate_count=1, delay_after_operation=0.5, *args, **kwargs) -> any:
    """处理弹窗面板

    Args:
        tpl_wait (Template): [description]
        func_suc ([type]): [description]
        func_fail ([type], optional): [description]. Defaults to None.
        lmt_operate_count (int, optional): [description]. Defaults to 1.
        delay_after_operation (int, optional): [description]. Defaults to 1.

    Returns:
        any: 返回tpl_wait的坐标点，或None
    """
    op_count = 0
    ret = None
    while True:
        dialog_pos = exists(tpl_wait)
        if dialog_pos:
            ret = dialog_pos
            if lmt_operate_count < 0 or op_count < lmt_operate_count:
                op_count += 1
                if ret:
                    hr = func_suc()
                    if hr and isinstance(hr, HandleResult):
                        hr.match_pos = ret
                        ret = hr
                        pass
                    pass
                else:
                    if func_fail:
                        func_fail()
                    pass
                pass
            sleep(delay_after_operation)
            pass
        else:
            break
    return ret


def on_handle_next_floor(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> any:
    tpl = Template(r"tpl1617017357016.png", record_pos=(-0.01, -0.032), resolution=(720, 1280))

    def func_suc() -> None:
        scene.map_discover(direction, NodeEnum.NEXT_FLOOR)
        if scene.game.is_full_map and not scene.is_map_clean():
            # 取消进入下一次. 等待全图探索完成, 自动追加下一次按钮
            touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
            pass
        else:
            # 进入下一层. 地图清空，不需要map_discover和map_move
            touch(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440)))
            # 等待2s, 等加载完成
            sleep(2)
            wait(Template(r"tpl1617102958252.png", record_pos=(-0.453, -0.724), resolution=(720, 1280)))
            sleep(2)
            scene.game.cur_floor += 1
            pass
    return on_handle_basic_dialog(tpl, func_suc)


def on_handle_altar(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> None:
    tpl = Template(r"tpl1617191129012.png", record_pos=(0.011, -0.325), resolution=(720, 1280))

    def func_suc() -> None:
        # 祭坛  TODO: 直接退出
        # if exists(Template(r"tpl1617191352726.png", rgb=True, record_pos=(0.0, 0.321), resolution=(720, 1280))):
        touch(Template(r"tpl1617191310309.png", record_pos=(0.024, 0.693), resolution=(720, 1280)))
        scene.map_discover(direction, NodeEnum.ALTAR)
        pass
    return on_handle_basic_dialog(tpl, func_suc)


def on_handle_sercet_space(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> None:
    tpl = Template(r"tpl1617202135423.png", record_pos=(-0.044, -0.028), resolution=(720, 1280))

    def func_suc() -> None:
        # 秘境, 不进.
        touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
        scene.map_discover(direction, NodeEnum.SPACE)
        pass
    return on_handle_basic_dialog(tpl, func_suc)


def on_handle_shop(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> None:
    tpl = Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280))

    def func_suc() -> None:
        scene.map_discover(direction, NodeEnum.SHOP)
        # 商店 - "退出"按钮  - TODO: 购买药瓶等逻辑
        touch(Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280)))
        pass
    return on_handle_basic_dialog(tpl, func_suc)


def on_handle_gold_box(scene: TdydxcScene, direction: Direction, *args, **kwargs) -> None:
    tpl = Template(r"tpl1617471061654.png", record_pos=(0.097, -0.022), resolution=(720, 1280))

    def func_suc() -> None:
        if scene.game.game_auto_open_gold_key_box:
            touch(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440)))
            scene.map_discover(direction, NodeEnum.EMPTY)
            Utility.LOGGER.info("打开箱子.")
            pass
        else:
            # 金箱子 - "取消"按钮  - TODO: 实现使用金钥匙的逻辑
            touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
            scene.map_discover(direction, NodeEnum.GOLD_KEY_BOX)
            Utility.LOGGER.info("取消箱子.")
            pass
        pass
    return on_handle_basic_dialog(tpl, func_suc)


def on_handle_unknown_node(scene: TdydxcScene, direction: Direction, image=None, *args, **kwargs) -> None:
    # 点击会移动的节点： 金币, 误判[宠物]等节点, 移除待排查列表
    # 点击不会移动的节点： 木箱子、宝石罐、金箱子、BUFF、青蛙祭坛、
    # 最后的保底, 需要根据情况判断
    scene.map_discover(direction, NodeEnum.EMPTY)
    # scene.map_draw()
    # tdydxc_map.map_node_recognition(image, scene.get_move_vector(direction), mark=True)
    # aircv.show_origin_size(image)
    Utility.LOGGER.warning("miss matched event.")
    return True


def on_game_battle(scene: TdydxcScene) -> None:
    btn_giveup = Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280))
    # 等待战斗结束
    while exists(btn_giveup):
        # TODO: 判断是否需要使用技能
        sleep(scene.game.game_operation_delay)
        pass
    return


def on_auto_battle() -> None:
    w, h = device().get_current_resolution()  # 获取手机分辨率
    game = TdydxcGame()
    game.screen_center_point = [0.5*w, 0.5*h]
    game.screen_point_cell_width = w/8
    game.is_full_map = True

    _floor = 0
    _battle_end = False
    while(not _battle_end):
        if _floor != game.cur_floor:
            # 需要重新初始化地图
            tdydxc = TdydxcScene()
            mini_map = snapshot_mini_map()
            tdydxc.init_mini_map(tdydxc_map.generate_mini_map(mini_map, mark=True))
            tdydxc.game = game
            # aircv.show_origin_size(mini_map)
            tdydxc.map_draw()
            _floor = game.cur_floor
            pass
        try:
            _next = tdydxc.nav_next_point()
            if not _next:
                break
            on_game_move_ex2(tdydxc, _next)
        except Exception as e:
            if tdydxc:
                tdydxc.map_draw()
                pass
            raise e
        pass
    Utility.LOGGER.info("battle end. scene: %s", game.cur_floor)
    if tdydxc:
        tdydxc.map_draw()
        pass
    return


def on_select_battle_map(mode_id: int, map_id: int, map_diff: int, level: int) -> None:
    """选中模式战斗

    Args:
        mode_id (int): [description]
        map_id (int): [description]
        map_diff (int): [description]
        level (int): [description]

    Raises:
        Exception: [description]
        Exception: [description]
        Exception: [description]
    """
    # 模式 [初心试炼, 勇者试炼]
    modes = {
        1: Template(r"tpl1617543705145.png", record_pos=(0.003, -0.738), resolution=(720, 1280), rgb=True),
        2: Template(r"tpl1617543657671.png", record_pos=(0.004, -0.744), resolution=(720, 1280), rgb=True),
    }
    # 地图 [绿先知，蛇，巨魔挖掘场, 龙骨, 暗夜城堡]
    maps = {
        1: Template(r"tpl1617543743636.png", record_pos=(0.268, -0.411), resolution=(720, 1280)),
        2: Template(r"tpl1617543749731.png", record_pos=(-0.256, -0.182), resolution=(720, 1280)),
        3: Template(r"tpl1617543758666.png", record_pos=(0.268, 0.028), resolution=(720, 1280)),
        4: Template(r"tpl1617543763794.png", record_pos=(-0.272, 0.243), resolution=(720, 1280)),
        5: Template(r"tpl1617543772341.png", record_pos=(0.229, 0.461), resolution=(720, 1280))
    }
    # 难度
    diffs = {
        1: Template(r"tpl1617543789134.png", record_pos=(-0.001, -0.185), resolution=(720, 1280), rgb=True),
        2: Template(r"tpl1617543822397.png", record_pos=(-0.001, -0.192), resolution=(720, 1280), rgb=True),
    }

    # 地图层 [1, 11, 21, 直接boss]
    levels = {
        1: Template(r"tpl1617543847863.png", record_pos=(-0.01, -0.013), resolution=(720, 1280)),
        2: Template(r"tpl1617543857853.png", record_pos=(-0.008, 0.138), resolution=(720, 1280)),
        3: Template(r"tpl1617543864919.png", record_pos=(0.01, 0.296), resolution=(720, 1280)),
        4: Template(r"tpl1617543873441.png", record_pos=(0.001, 0.46), resolution=(720, 1280)),
    }
    tpl_mode = modes.get(mode_id)
    if not tpl_mode:
        raise Exception("tdydxc unsupport mode:{}".format(mode_id))
    while not exists(Template(r"tpl1617543705145.png", record_pos=(0.003, -0.738), resolution=(720, 1280), rgb=True)):
        # 滑动切换地图
        touch(Template(r"tpl1617546891925.png", record_pos=(-0.383, -0.754), resolution=(720, 1280)))
        sleep(1)
        pass
    tpl_map = maps.get(map_id)
    if not tpl_map:
        raise Exception("tdydxc unsupport map:{}".format(map_id))
    touch(tpl_map)
    tpl_map_diff = diffs.get(map_diff)
    if not tpl_map_diff:
        raise Exception("tdydxc unsupport map:{}".format(map_id))
    while not exists(tpl_map_diff):
        touch(Template(r"tpl1617543796358.png", record_pos=(0.369, -0.178), resolution=(720, 1280)))
        pass
    tpl_lvl = levels.get(level)
    pos_lvl = exists(tpl_lvl)
    if pos_lvl:
        touch(pos_lvl)

        # 挑战BOSS, 出现确认按钮.
        if level == 4:
            pos_confirm = exists(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440)))
            if pos_confirm:
                touch(pos_confirm)
                pass
            pass
        touch(Template(r"tpl1615902050254.png", record_pos=(-0.033, 0.803), resolution=(811, 1440)))
        touch(Template(r"tpl1615902052185.png", record_pos=(-0.033, 0.803), resolution=(811, 1440)))
        pass
    # 找到合适和地图. 等待加载完成
    sleep(2)
    wait(Template(r"tpl1617102958252.png", record_pos=(-0.453, -0.724), resolution=(720, 1280)))
    sleep(2)
    return


def on_battle_change_bonfire() -> None:
    """调整灯火亮度.
    """
    touch(Template(r"tpl1615902058574.png", record_pos=(0.438, -0.564), resolution=(811, 1440)))
#     while not exists(Template(r"tpl1616159184068.png", rgb=True, record_pos=(0.171, 0.482), resolution=(720, 1280))):
    for x in range(4):
        touch(Template(r"tpl1615902061934.png", record_pos=(0.163, 0.506), resolution=(811, 1440)))
        touch(Template(r"tpl1615902063423.png", record_pos=(-0.183, 0.226), resolution=(811, 1440)))
        pass
    touch(Template(r"tpl1615902073472.png", record_pos=(0.018, 0.8), resolution=(811, 1440)))
    pass


# touch(Template(r"tpl1616073759155.png", record_pos=(-0.079, 0.475), resolution=(720, 1280)))
# on_select_battle_map(1, 3, 2, 1)
# # aircv.show_origin_size(snapshot_mini_map())
# on_battle_change_bonfire()
# sleep(3)
on_auto_battle()
aircv.show_origin_size(snapshot_mini_map())


# def on_auto_kill_boss_task():
#     """自动挑战BOSS
#     """
#     touch(Template(r"tpl1616073759155.png",
#                    record_pos=(-0.079, 0.475), resolution=(720, 1280)))
#     touch(Template(r"tpl1615902044737.png", record_pos=(
#         0.295, -0.005), resolution=(811, 1440)))
#     touch(Template(r"tpl1615902046273.png",
#                    record_pos=(-0.04, 0.464), resolution=(811, 1440)))
#     touch(Template(r"tpl1615902047920.png",
#                    record_pos=(-0.204, 0.218), resolution=(811, 1440)))
#     touch(Template(r"tpl1615902050254.png",
#                    record_pos=(-0.033, 0.803), resolution=(811, 1440)))
#     touch(Template(r"tpl1615902052185.png",
#                    record_pos=(-0.033, 0.803), resolution=(811, 1440)))

#     on_battle_change_bonfire()

#     # 计算右中间位置的坐标，两次开始战斗。
#     w, h = device().get_current_resolution()  # 获取手机分辨率
#     screen_mid_point = [0.5*w, 0.5*h]
#     cell_width = w/8

#     btn_giveup = Template(r"tpl1616074069208.png",
#                           record_pos=(-0.008, 0.376), resolution=(720, 1280))
#     while not exists(btn_giveup):
#         swipe(screen_mid_point, vector=[0.3, 0.0015])
#         sleep(1)
#         pass
#     # 等待战斗结束
#     while exists(btn_giveup):
#         sleep(3)
#         pass

#     sleep(2)
#     # 拾取战利品

#     # touch([0.5*w + 0.125*w, 0.5*h + 0.125*h])#点击手机中心位置
#     print("mid point:", screen_mid_point)
#     print("cell_width:", cell_width)

#     def func_move_by_swipe(point, cell_width, vec):
#         p = (point[0] + vec[0] * cell_width, point[1] + vec[1] * cell_width)
#         print("touch point:",  p)
#         touch(p)
#         sleep(1)
#         pass

#     vec_array = [[0, -1], [0, 1], [0, 1], [0, -1], [1, 0], [0, -1], [0, -1], [1, 0], [0, 1], [0, 1], [0, 1],
#                  [0, 1], [0, 1], [-1, 0], [0, -1], [0, -1], [0, -1], [1, 0], [1, 0], [0, 1], [0, -1], [0, -1], [0, 1]]
#     for vec in vec_array:
#         func_move_by_swipe(screen_mid_point, cell_width, vec)
#         pass

#     # 中间继续右直行
#     while not exists(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440))):
#         swipe(screen_mid_point, vector=[0.1, 0])
#         pass
#     touch(Template(r"tpl1615902133396.png",
#                    record_pos=(-0.209, 0.231), resolution=(811, 1440)))
#     touch(Template(r"tpl1615902135599.png", record_pos=(
#         0.01, 0.71), resolution=(811, 1440)))
#     pass


# 搜索右上角小地图. 确定黑色不可行动的区域.  12*12
# lookup(, (530, 30, 720, 190))


# print(loop_find(Template(r"tpl1616404376736.png", record_pos=(0.438, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404431747.png", record_pos=(0.365, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404419462.png", record_pos=(0.324, -0.797), resolution=(720, 1280))))

