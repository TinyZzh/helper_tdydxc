# -*- encoding=utf8 -*-
__author__ = "TinyZ"



from airtest.core.api import *
from airtest.core.cv import loop_find
from airtest.aircv import *
from GameHelper.core.helper.images import screen_snapshot


def get_point_rgb_value(screen, point):
    # 位于屏幕中[x, y]位置的点的rgb值的获取：(x,y均从0计数)
    # 注意：这里拿到的颜色是bgr，而非rgb
    x, y = point
    bgr = screen[y][x]
    return bgr[...,::-1]


def get_multi_point_bgr_value(screen, *args):
    _result = []
    for arg in args:
        _result.append(get_point_rgb_value(screen, arg))
        pass
    return _result

def lookup_rect_image(screen, rect):
    return aircv.crop_image(screen, rect)

_screen = device().snapshot()
cut_img = screen_snapshot(_screen, [530, 30, 720, 190])
tpl = Template(r"tpl1616404431747.png", record_pos=(0.365, -0.751), resolution=(720, 1280))
print("match in", tpl.match_in(cut_img))
print(get_point_rgb_value(cut_img, (1, 1)))










def func_low_bonfire():
    touch(Template(r"tpl1615902058574.png", record_pos=(0.438, -0.564), resolution=(811, 1440)))
#     while not exists(Template(r"tpl1616159184068.png", rgb=True, record_pos=(0.171, 0.482), resolution=(720, 1280))):
    for x in range(4):
        touch(Template(r"tpl1615902061934.png", record_pos=(0.163, 0.506), resolution=(811, 1440)))
        touch(Template(r"tpl1615902063423.png", record_pos=(-0.183, 0.226), resolution=(811, 1440)))
        pass
    touch(Template(r"tpl1615902073472.png", record_pos=(0.018, 0.8), resolution=(811, 1440)))
    pass


def func_auto_task():
    touch(Template(r"tpl1616073759155.png", record_pos=(-0.079, 0.475), resolution=(720, 1280)))
    touch(Template(r"tpl1615902044737.png", record_pos=(0.295, -0.005), resolution=(811, 1440)))
    touch(Template(r"tpl1615902046273.png", record_pos=(-0.04, 0.464), resolution=(811, 1440)))
    touch(Template(r"tpl1615902047920.png", record_pos=(-0.204, 0.218), resolution=(811, 1440)))
    touch(Template(r"tpl1615902050254.png", record_pos=(-0.033, 0.803), resolution=(811, 1440)))
    touch(Template(r"tpl1615902052185.png", record_pos=(-0.033, 0.803), resolution=(811, 1440)))

    func_low_bonfire()

    ### 计算右中间位置的坐标，两次开始战斗。
    w,h=device().get_current_resolution()#获取手机分辨率
    screen_mid_point = [0.5*w, 0.5*h]
    cell_width = w/8

    btn_giveup = Template(r"tpl1616074069208.png", record_pos=(-0.008, 0.376), resolution=(720, 1280))
    while not exists(btn_giveup):
        swipe(screen_mid_point, vector = [0.3, 0.0015])
        sleep(1)
        pass
    # 等待战斗结束
    while exists(btn_giveup):
        sleep(3)
        pass

    sleep(2)
    ## 拾取战利品

    # touch([0.5*w + 0.125*w, 0.5*h + 0.125*h])#点击手机中心位置
    print("mid point:", screen_mid_point)
    print("cell_width:", cell_width)
    def func_move_by_swipe(point, cell_width, vec):
        p = (point[0] + vec[0] * cell_width, point[1] + vec[1] * cell_width)
        print("touch point:",  p)
        touch(p)
        sleep(1)
        pass

    vec_array = [[0, -1], [0, 1], [0, 1], [0, -1], [1, 0], [0, -1], [0, -1], [1, 0], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [-1, 0], [0, -1], [0, -1], [0, -1], [1, 0], [1, 0], [0, 1], [0, -1], [0, -1], [0, 1]]
    for vec in vec_array:
        func_move_by_swipe(screen_mid_point, cell_width, vec)
        pass

    ##  中间继续右直行 
    while not exists(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440))):
        swipe(screen_mid_point, vector=[0.1, 0])
        pass
    touch(Template(r"tpl1615902133396.png", record_pos=(-0.209, 0.231), resolution=(811, 1440)))
    touch(Template(r"tpl1615902135599.png", record_pos=(0.01, 0.71), resolution=(811, 1440)))
    pass


# 搜索右上角小地图. 确定黑色不可行动的区域.  12*12
# lookup(, (530, 30, 720, 190))



# print(loop_find(Template(r"tpl1616404376736.png", record_pos=(0.438, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404431747.png", record_pos=(0.365, -0.751), resolution=(720, 1280))))
# print(loop_find(Template(r"tpl1616404419462.png", record_pos=(0.324, -0.797), resolution=(720, 1280))))





while True:
    func_auto_task()
    pass



