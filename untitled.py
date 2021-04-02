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
    sleep(1)
    # TODO: 是否弹出交互界面
    node = scene.get_click_point(direction)
    if node.state == NodeEnum.CLICK:
        handlers = [
            on_handle_battle,
            on_handle_next_floor,
            on_handle_altar,
            on_handle_sercet_space,
            on_handle_shop,
            on_handle_unknown_node,
        ]
        for h in handlers:
            if h(scene, direction, before_snapshot):
                Utility.LOGGER.info("handle event:%s, direction:%s", h.__class__, direction)
                break
            pass
        pass
    elif node.state == NodeEnum.NEXT_FLOOR:
        on_handle_next_floor(scene, direction, before_snapshot)
        pass
    elif node.state == NodeEnum.ALTAR:
        on_handle_altar(scene, direction, before_snapshot)
        pass

    # TODO: 判断是否移动成功
    # 原理：模拟点击屏幕前，截取小地图中心点的方块图片. 点击后，截图小地图，再根据点击坐标反向获取移动前位置的的截图。截图一致时，说明点击未触发移动
    #
    before_nodes = tdydxc_map.parse_mini_map(before_snapshot)
    after_snapshot = snapshot_mini_map()
    after_nodes = tdydxc_map.parse_mini_map(after_snapshot)
    # w, h = before_nodes.shape
    # match = {
    #     Direction.TOP: lambda ary0, ary1: [np.delete(ary0, 0, axis=1), np.delete(ary1, h-1, axis=1)],
    #     Direction.BOTTOM: lambda ary0, ary1: [np.delete(ary0, h-1, axis=1), np.delete(ary1, 0, axis=1)],
    #     Direction.LEFT: lambda ary0, ary1: [np.delete(ary0, w-1, axis=0), np.delete(ary1, 0, axis=0)],
    #     Direction.RIGHT: lambda ary0, ary1: [np.delete(ary0, 0, axis=0), np.delete(ary1, w-1, axis=0)],
    # }
    # sub_a, sub_b = match[direction](before_nodes, after_nodes)
    w, h = before_nodes.shape
    scene.map_draw_ex(before_nodes)
    scene.map_draw_ex(after_nodes)

    # 地图点变化超过6个， 判定为已移动
    diff = sum([1 if before_nodes[i][j] != after_nodes[i][j] else 0 for i in range(w) for j in range(h)])
    Utility.LOGGER.error("diff:%s, shape:%s", diff, (w, h))
    if diff > 6:
        # 等待移动完成. 优化一下判断逻辑. 有可能卡住导致移动失败
        scene.map_move(tdydxc_map.map_node_recognition_with_direction(after_snapshot, direction), direction)
        pass

    scene.map_draw()
    aircv.show_origin_size(after_snapshot)

    pass


def on_handle_battle(scene: TdydxcScene, direction: Direction, image=None) -> any:
    pos = exists(Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280)))
    if pos:
        # 进入战斗, 等待战斗胜利.
        # 有可能出现秒杀，耗时短, 必须优先判断
        on_game_battle(scene)
        scene.map_discover(direction, NodeEnum.EMPTY)
        pass
    return pos


def on_handle_next_floor(scene: TdydxcScene, direction: Direction, image=None) -> any:
    pos = exists(Template(r"tpl1617017357016.png", record_pos=(-0.01, -0.032), resolution=(720, 1280)))
    if pos:
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
            scene.game.cur_floor += 1
            pass
    return pos


def on_handle_altar(scene: TdydxcScene, direction: Direction, image=None) -> None:
    pos = exists(Template(r"tpl1617191129012.png", record_pos=(0.011, -0.325), resolution=(720, 1280)))
    if pos:
        # 祭坛  TODO: 直接退出
        # if exists(Template(r"tpl1617191352726.png", rgb=True, record_pos=(0.0, 0.321), resolution=(720, 1280))):
        touch(Template(r"tpl1617191310309.png", record_pos=(0.024, 0.693), resolution=(720, 1280)))
        scene.map_discover(direction, NodeEnum.ALTAR)
        pass
    return pos


def on_handle_sercet_space(scene: TdydxcScene, direction: Direction, image=None) -> None:
    pos = exists(Template(r"tpl1617202135423.png", record_pos=(-0.044, -0.028), resolution=(720, 1280)))
    if pos:
        # 秘境, 不进.
        touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
        scene.map_discover(direction, NodeEnum.SPACE)
        pass
    return pos


def on_handle_shop(scene: TdydxcScene, direction: Direction, image=None) -> None:
    pos = exists(Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280)))
    if pos:
        scene.map_discover(direction, NodeEnum.SHOP)
        # 商店 - "退出"按钮  - TODO: 购买药瓶等逻辑
        touch(Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280)))
        pass
    return pos


def on_handle_unknown_node(scene: TdydxcScene, direction: Direction, mini_map=None) -> None:
    # 点击会移动的节点： 金币, 误判[宠物]等节点, 移除待排查列表
    # 点击不会移动的节点： 木箱子、宝石罐、金箱子、BUFF、青蛙祭坛、
    # 最后的保底, 需要根据情况判断
    scene.map_discover(direction, NodeEnum.EMPTY)
    # scene.map_draw()
    # tdydxc_map.map_node_recognition(mini_map, scene.get_move_vector(direction), mark=True)
    aircv.show_origin_size(mini_map)
    Utility.LOGGER.warning("miss matched event.")
    return True


# def on_game_move_ex(scene: TdydxcScene, direction: Direction) -> None:
#     key_rect = [48, 48, 116, 116]
#     before_snapshot = snapshot_mini_map()
#     draw_rect_point = scene.get_move_vector(direction)
#     tdydxc_map.map_draw_rectangle(before_snapshot, draw_rect_point)
#     aircv.show_origin_size(screen_snapshot(before_snapshot, key_rect))

#     rel_p = scene.get_screen_point(direction)
#     touch(rel_p)
#     sleep(1)
#     # TODO: 是否弹出交互界面

#     # TODO: 判断是否移动成功
#     # 原理：模拟点击屏幕前，截取小地图中心点的方块图片. 点击后，截图小地图，再根据点击坐标反向获取移动前位置的的截图。截图一致时，说明点击未触发移动
#     #
#     mini_map = snapshot_mini_map()
#     tdydxc_map.map_draw_rectangle(mini_map, draw_rect_point)
#     match_result = AirImage(screen_snapshot(before_snapshot, key_rect), rgb=True).match(screen_snapshot(mini_map, key_rect))
#     Utility.LOGGER.error("匹配结果: %s", match_result)
#     aircv.show_origin_size(screen_snapshot(mini_map, key_rect))
#     if match_result:
#         # 移动
#         scene.map_move(mini_map, direction)
#         pass
#     else:
#         pass
#     aircv.show_origin_size(mini_map)
#     vec = scene.get_move_vector(direction)
#     after = tdydxc_map.parse_mini_map(mini_map)
#     scene.map_draw_ex(after)
#     w, h = after.shape
#     match = {
#         Direction.TOP: lambda arr: np.delete(arr, 0, axis=1),
#         Direction.BOTTOM: lambda arr: np.delete(arr, h-1, axis=1),
#         Direction.LEFT: lambda arr: np.delete(arr, w-1, axis=0),
#         Direction.RIGHT: lambda arr: np.delete(arr, 0, axis=0),
#     }
#     rect = match[direction](after)
#     Utility.LOGGER.info("剪切后的小图: %s", direction.name)
#     scene.map_draw_ex(rect)
#     scene.map_draw()
#     aircv.show_origin_size(mini_map)
#     pass


def on_game_move(scene: TdydxcScene, direction: Direction):
    # 移动一个格子. 坐标识别比较困难
    rel_p = scene.get_screen_point(direction)
    print("touch point:{}".format(rel_p))
    _prev_mini_map = tdydxc_map.parse_mini_map(snapshot_mini_map())
    touch(rel_p)
    sleep(1)
    # 根据点击的反馈确定目标类型
    mini_map = snapshot_mini_map()
    if mini_map == _prev_mini_map:
        print("移动失败")
        scene.map_draw()
        aircv.show_origin_size(mini_map)
        return
    node = scene.get_click_point(direction)
    print("player move to:{}".format(node))
    if node.state == NodeEnum.EMPTY:
        # 等待移动完成. 优化一下判断逻辑. 有可能卡住导致移动失败
        scene.map_move(mini_map, direction)
        pass
    elif node.state == NodeEnum.CLICK:
        if exists(Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280))):
            # 进入战斗, 等待战斗胜利.
            # 有可能出现秒杀，耗时短, 必须优先判断
            on_game_battle(scene)
            scene.map_discover(direction, NodeEnum.EMPTY)
            pass
        elif exists(Template(r"tpl1617017357016.png", record_pos=(-0.01, -0.032), resolution=(720, 1280))):
            scene.map_discover(direction, NodeEnum.NEXT_FLOOR)
            scene.map_move(mini_map, direction)
            if scene.game.is_full_map and not scene.is_map_clean():
                # 先取消进去下一次. 等待全图探索完成, 自动追加下一次按钮
                touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
                pass
            else:
                # 进入下一层. 地图清空，不需要map_discover和map_move
                touch(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440)))
                # 等待2s, 等加载完成
                sleep(2)
                wait(Template(r"tpl1617102958252.png", record_pos=(-0.453, -0.724), resolution=(720, 1280)))
                scene.game.cur_floor += 1
                pass
        elif exists(Template(r"tpl1617191129012.png", record_pos=(0.011, -0.325), resolution=(720, 1280))):
            # 祭坛  TODO: 直接退出
            # if exists(Template(r"tpl1617191352726.png", rgb=True, record_pos=(0.0, 0.321), resolution=(720, 1280))):
            touch(Template(r"tpl1617191310309.png", record_pos=(0.024, 0.693), resolution=(720, 1280)))
            scene.map_discover(direction, NodeEnum.ALTAR)
            pass
        elif exists(Template(r"tpl1617202135423.png", record_pos=(-0.044, -0.028), resolution=(720, 1280))):
            # 秘境, 不进.
            touch(Template(r"tpl1617101341321.png", record_pos=(0.206, 0.242), resolution=(720, 1280)))
            scene.map_discover(direction, NodeEnum.SPACE)
            scene.map_move(mini_map, direction)
            pass
        elif exists(Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280))):
            scene.map_discover(direction, NodeEnum.SHOP)
            # 商店 - "退出"按钮  - TODO: 购买药瓶等逻辑
            touch(Template(r"tpl1617017094719.png", record_pos=(0.29, 0.811), resolution=(720, 1280)))
            pass
        else:
            # 点击会移动的节点： 金币, 误判[宠物]等节点, 移除待排查列表
            # 点击不会移动的节点： 木箱子、宝石罐、金箱子、BUFF、青蛙祭坛、
            scene.map_discover(direction, NodeEnum.EMPTY)
            scene.map_move(mini_map, direction)
            scene.map_draw()
            tdydxc_map.map_node_recognition(mini_map, scene.get_move_vector(direction), mark=True)
            aircv.show_origin_size(mini_map)
            pass
        pass
    elif node.state == NodeEnum.CLICK_BLOCK:
        scene.map_discover(direction, NodeEnum.EMPTY)
        scene.map_draw()
        aircv.show_origin_size(mini_map)
        pass
    else:
        scene.map_draw()
        aircv.show_origin_size(mini_map)
        pass
    # print(scene.get_nodes())
    # aircv.show_origin_size(mini_map)
    return


def on_game_battle(scene: TdydxcScene) -> None:
    btn_giveup = Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280))
    # 等待战斗结束
    while exists(btn_giveup):
        # TODO: 判断是否需要使用技能
        sleep(1)
        pass
    sleep(1)
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
            tdydxc.map_draw()
            aircv.show_origin_size(mini_map)
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


on_auto_battle()
aircv.show_origin_size(snapshot_mini_map())


def on_battle_change_bonfire() -> None:
    """调整灯火亮度.
    """
    touch(Template(r"tpl1615902058574.png", record_pos=(
        0.438, -0.564), resolution=(811, 1440)))
#     while not exists(Template(r"tpl1616159184068.png", rgb=True, record_pos=(0.171, 0.482), resolution=(720, 1280))):
    for x in range(4):
        touch(Template(r"tpl1615902061934.png", record_pos=(
            0.163, 0.506), resolution=(811, 1440)))
        touch(Template(r"tpl1615902063423.png",
                       record_pos=(-0.183, 0.226), resolution=(811, 1440)))
        pass
    touch(Template(r"tpl1615902073472.png", record_pos=(
        0.018, 0.8), resolution=(811, 1440)))
    pass


def on_auto_kill_boss_task():
    """自动挑战BOSS
    """
    touch(Template(r"tpl1616073759155.png",
                   record_pos=(-0.079, 0.475), resolution=(720, 1280)))
    touch(Template(r"tpl1615902044737.png", record_pos=(
        0.295, -0.005), resolution=(811, 1440)))
    touch(Template(r"tpl1615902046273.png",
                   record_pos=(-0.04, 0.464), resolution=(811, 1440)))
    touch(Template(r"tpl1615902047920.png",
                   record_pos=(-0.204, 0.218), resolution=(811, 1440)))
    touch(Template(r"tpl1615902050254.png",
                   record_pos=(-0.033, 0.803), resolution=(811, 1440)))
    touch(Template(r"tpl1615902052185.png",
                   record_pos=(-0.033, 0.803), resolution=(811, 1440)))

    on_battle_change_bonfire()

    # 计算右中间位置的坐标，两次开始战斗。
    w, h = device().get_current_resolution()  # 获取手机分辨率
    screen_mid_point = [0.5*w, 0.5*h]
    cell_width = w/8

    btn_giveup = Template(r"tpl1616074069208.png",
                          record_pos=(-0.008, 0.376), resolution=(720, 1280))
    while not exists(btn_giveup):
        swipe(screen_mid_point, vector=[0.3, 0.0015])
        sleep(1)
        pass
    # 等待战斗结束
    while exists(btn_giveup):
        sleep(3)
        pass

    sleep(2)
    # 拾取战利品

    # touch([0.5*w + 0.125*w, 0.5*h + 0.125*h])#点击手机中心位置
    print("mid point:", screen_mid_point)
    print("cell_width:", cell_width)

    def func_move_by_swipe(point, cell_width, vec):
        p = (point[0] + vec[0] * cell_width, point[1] + vec[1] * cell_width)
        print("touch point:",  p)
        touch(p)
        sleep(1)
        pass

    vec_array = [[0, -1], [0, 1], [0, 1], [0, -1], [1, 0], [0, -1], [0, -1], [1, 0], [0, 1], [0, 1], [0, 1],
                 [0, 1], [0, 1], [-1, 0], [0, -1], [0, -1], [0, -1], [1, 0], [1, 0], [0, 1], [0, -1], [0, -1], [0, 1]]
    for vec in vec_array:
        func_move_by_swipe(screen_mid_point, cell_width, vec)
        pass

    # 中间继续右直行
    while not exists(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440))):
        swipe(screen_mid_point, vector=[0.1, 0])
        pass
    touch(Template(r"tpl1615902133396.png",
                   record_pos=(-0.209, 0.231), resolution=(811, 1440)))
    touch(Template(r"tpl1615902135599.png", record_pos=(
        0.01, 0.71), resolution=(811, 1440)))
    pass


# 搜索右上角小地图. 确定黑色不可行动的区域.  12*12
# lookup(, (530, 30, 720, 190))


# print(loop_find(Template(r"tpl1616404376736.png", record_pos=(0.438, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404431747.png", record_pos=(0.365, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404419462.png", record_pos=(0.324, -0.797), resolution=(720, 1280))))





